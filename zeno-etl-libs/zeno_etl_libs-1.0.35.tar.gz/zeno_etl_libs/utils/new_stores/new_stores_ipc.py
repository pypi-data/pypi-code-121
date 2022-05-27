"""
Author - Shubham Jangir (shubham.jangir@zeno.health)
Objective   - New stores (1 to 3 month) safety stock algo
            - Any corrections to be input here in module
            - After this module, mysql update to be run
"""

from datetime import datetime
from datetime import timedelta

from zeno_etl_libs.db.db import PostGre

from scipy.stats import norm

from zeno_etl_libs.utils.new_stores.new_store_stock_triggers import *
from zeno_etl_libs.utils.new_stores.helper_functions import *


def new_stores_ss_calc(store_id, run_date, db, schema, logger):
    #####################################################
    # Final function for new stores (1-3 months) safety stock
    # Combines base and triggers algorithm
    #####################################################
    # Get demand
    data_demand = get_demand(store_id, db, schema)

    # Get lead time
    data_lt, lt_store_mean, lt_store_std = get_lead_time(store_id, run_date)

    # Service level - hardcoded
    service_level = 0.95
    z = norm.ppf(service_level)

    #####################################################
    # SS calculation - Base algo
    #####################################################
    data = ss_calc(data_demand, data_lt, lt_store_mean, lt_store_std, z, db, schema)
    data['algo_type'] = 'base'

    logger.info("Length Base algo data {}".format(len(data)))

    # Max>0
    data_forecast_pos = data[data['max'] > 0].copy()
    logger.info("Length Base algo forecast positive - data {}".format(len(data_forecast_pos)))

    #####################################################
    # Triggers
    #####################################################
    # Put max==0 logic here, and pass those drug-ids, for given store
    data_algo_max0 = data[data['max'] == 0][['drug_id']].drop_duplicates()
    data_algo_max0_list = data_algo_max0['drug_id'].to_list()
    logger.info("Max 0 drugs from base algo, length is {}".format(len(data_algo_max0_list)))
    # But this is max0 from base algo, there maybe other max0 in drug-order-info
    # Fetching them
    # Formatted SQL queries
    q_max0 = query_max_zero(store_id, schema)
    data_doi_max0 = prep_data_from_sql(q_max0, db)
    data_doi_max0 = data_doi_max0[['drug_id']].drop_duplicates()
    logger.info("Max 0 drugs from mysql drug-order-info, length is {}".format(len(data_doi_max0)))

    # Remove drugs for which forecast is already positive
    data_forecast_pos_list = data_forecast_pos['drug_id'].drop_duplicates().to_list()
    data_doi_max0_forecast0 = data_doi_max0[~data_doi_max0['drug_id'].isin(data_forecast_pos_list)]

    logger.info("Max 0 drugs from mysql drug-order-info, after removing forecast positive,"
                "length is {}".format(len(data_doi_max0_forecast0)))

    # Append both and take unique
    data_doi_max0_forecast0_append = data_doi_max0_forecast0[~data_doi_max0_forecast0['drug_id'].isin(
        data_algo_max0_list)]
    logger.info("Max 0 drugs from mysql drug-order-info, non overlapping with forecast 0, "
                "length is {}".format(len(data_doi_max0_forecast0_append)))

    max0_drugs_df = data_algo_max0.append(data_doi_max0_forecast0_append)
    max0_drugs_df = max0_drugs_df.drop_duplicates(subset='drug_id')
    logger.info("Final Max 0 drugs, length is {}".format(len(max0_drugs_df)))

    triggers_data, triggers_summary, \
        triggers_store_report = triggers_combined(store_id, run_date,
                                                  max0_drugs_df, db, schema)
    triggers_data = triggers_data[['drug_id', 'min', 'safety_stock', 'max']]
    triggers_data['algo_type'] = 'non_sales_triggers'

    # Output to s3 bucket
    # triggers_summary.to_csv(output_dir_path + f'triggers_summary_{store_id}_{run_date}.csv',
    #                         index=False)
    # triggers_store_report.to_csv(output_dir_path +
    #                              f'triggers_store_report_{store_id}_{run_date}.csv', index=False)

    logger.info("Length Triggers algo data raw {}".format(len(triggers_data)))

    # Remove those that are already part of base algo and already max>0
    drugs_base = data_forecast_pos['drug_id'].drop_duplicates().to_list()

    # Overlapping
    triggers_data_overlap = triggers_data[triggers_data['drug_id'].isin(drugs_base)]

    logger.info("Length triggers algo data overlapping {}".format(len(triggers_data_overlap)))

    triggers_data_append = triggers_data[~triggers_data['drug_id'].isin(drugs_base)]

    logger.info("Length triggers algo data non-overlapping {}".format(len(triggers_data_append)))

    # Append base algo, and triggers algo output
    data_final = data_forecast_pos.append(triggers_data_append)

    logger.info("Length data final {}".format(len(data_final)))

    # Put store id
    data_final['store_id'] = store_id

    # Final schema
    data_final = data_final[['store_id', 'drug_id', 'min', 'safety_stock', 'max', 'algo_type']]

    return data_final


def get_demand(store_id, db, schema):
    # sales query
    q_sales = f"""
           select "store-id", "drug-id", date("created-at") as "sales-date",
                   sum("net-quantity") as "net-sales-quantity"
           from "{schema}".sales s
           where "store-id" = {store_id}
           group by "store-id", "drug-id", "sales-date"
           """
    data_s = db.get_df(q_sales)
    data_s.columns = [c.replace('-', '_') for c in data_s.columns]
    data_s['sales_date'] = pd.to_datetime(data_s['sales_date'])

    # cfr pr loss
    q_cfr_pr = f"""
            select "store-id", "drug-id", 
                "attributed-loss-date" as "sales-date",
                sum("loss-quantity") as "loss-quantity"
            from "{schema}"."cfr-patient-request"
            where "store-id" = {store_id}
            and "drug-id" > 0
            and "loss-quantity" > 0
            group by  "store-id", "drug-id", "attributed-loss-date"
            """
    data_cfr_pr = db.get_df(q_cfr_pr)
    data_cfr_pr["loss-quantity"] = data_cfr_pr["loss-quantity"].astype(float)
    data_cfr_pr['sales-date'] = pd.to_datetime(data_cfr_pr['sales-date'])
    data_cfr_pr.columns = [c.replace('-', '_') for c in data_cfr_pr.columns]

    # Merge
    merge_data = data_s.merge(data_cfr_pr, how='outer', on=['store_id', 'drug_id', 'sales_date'])

    for i in ['net_sales_quantity', 'loss_quantity']:
        merge_data[i] = merge_data[i].fillna(0)

    merge_data['demand_quantity'] = merge_data['net_sales_quantity'] + merge_data['loss_quantity']

    data_demand = merge_data.groupby(['drug_id', 'sales_date'])['demand_quantity'].sum().reset_index()
    data_demand = data_demand.sort_values(by=['drug_id', 'sales_date'])

    return data_demand


def get_lead_time(store_id, run_date):
    # Shortbook is normally created after some delay, of actual trigger event
    sb_creation_delay_ethical = 1
    sb_creation_delay_other = 1
    sb_creation_delay_generic = 2

    # Fetch data last 'N' days
    end_date = str(datetime.strptime(run_date, '%Y-%m-%d') - timedelta(7))
    begin_date = str(datetime.strptime(run_date, '%Y-%m-%d') - timedelta(97))

    # ==== TEMP READ FROM PG ====
    pg = PostGre()
    pg.open_connection()
    # ===========================

    lead_time_query = '''
        select
            store_id,
            drug_id,
            drug_type,
            status,
            created_at,
            received_at
        from
            ops_fulfillment
        where
            request_type = 'Auto Short'
            and store_id = {store_id}
            and created_at <= '{end_date}'
            and created_at >= '{begin_date}'
            and status not in ('failed', 'deleted')
    '''.format(
        store_id=store_id, end_date=end_date, begin_date=begin_date)
    lead_time = pd.read_sql_query(lead_time_query, pg.connection)

    # Convert null received at, to true null
    lead_time['created_at'] = pd.to_datetime(lead_time['created_at'])
    lead_time['received_at'].replace({'0000-00-00 00:00:00': ''}, inplace=True)
    lead_time['received_at'] = pd.to_datetime(lead_time['received_at'])

    # Calculate lead time
    lead_time['lead_time'] = (lead_time['received_at'] -
                              lead_time['created_at']).astype('timedelta64[h]') / 24

    # Missing value impute
    lead_time['lead_time'].fillna(7, inplace=True)

    # Incorporate delay values
    lead_time['lead_time'] = np.select(
        [lead_time['drug_type'] == 'generic',
         lead_time['drug_type'] == 'ethical'],
        [lead_time['lead_time'] + sb_creation_delay_generic,
         lead_time['lead_time'] + sb_creation_delay_ethical],
        default=lead_time['lead_time'] + sb_creation_delay_other
    )

    # Store averages
    lt_store_mean = round(lead_time.lead_time.mean(), 2)
    lt_store_std = round(lead_time.lead_time.std(ddof=0), 2)

    # Summarize at drug level
    lt_drug = lead_time.groupby('drug_id'). \
        agg({'lead_time': [np.mean, np.std]}).reset_index()
    lt_drug.columns = ['drug_id', 'lead_time_mean', 'lead_time_std']

    # Impute for std missing
    lt_drug['lead_time_std'] = np.where(
        lt_drug['lead_time_std'].isin([0, np.nan]),
        lt_store_std, lt_drug['lead_time_std']
    )

    # ===== CLOSE PG =====
    pg.close_connection()
    # ====================

    return lt_drug, lt_store_mean, lt_store_std


def ss_calc(data_demand, data_lt, lt_store_mean, lt_store_std, z, db, schema):
    # Drug type restrictions if any
    q_drugs = f"""
        select
        id as "drug-id", type
        from "{schema}".drugs 
        """
    # where `type` in ('ethical','generic')
    data_drugs = db.get_df(q_drugs)
    data_drugs.columns = [c.replace('-', '_') for c in data_drugs.columns]

    # Avg and standard deviation demand
    data_demand_min_date = data_demand['sales_date'].min()
    data_demand_max_date = data_demand['sales_date'].max()

    # Create full demand list, across all calendar dates, drug_id level
    drugs = data_demand[['drug_id']].drop_duplicates()

    dates = pd.DataFrame({'sales_date': pd.date_range(data_demand_min_date, data_demand_max_date, freq='D')})

    drugs['key'] = 0
    dates['key'] = 0

    drug_dates = drugs[['drug_id', 'key']].merge(dates, on='key', how='outer')[['drug_id', 'sales_date']]

    data_demand_all = drug_dates.merge(data_demand, how='left', on=['drug_id', 'sales_date'])
    data_demand_all['demand_quantity'] = data_demand_all['demand_quantity'].fillna(0)

    # Merge with drugs master
    data_demand_all = data_demand_all.merge(data_drugs, how='left', on='drug_id')

    # Treat outliers
    '''
    data_demand_all['demand_quantity'] = np.where(data_demand_all['demand_quantity'] > 20,
                                                  np.log(data_demand_all['demand_quantity']),
                                                  data_demand_all['demand_quantity'])
    '''

    # Calculate demand mean and std
    data_demand_all_mean_std = data_demand_all.groupby(['drug_id', 'type'])['demand_quantity'].agg(
        ['mean', 'std']).reset_index()
    data_demand_all_mean_std = data_demand_all_mean_std.rename(columns={'mean': 'demand_mean',
                                                                        'std': 'demand_std'})

    # Merge with lead time mean and std
    data = data_demand_all_mean_std.merge(data_lt, how='left', on='drug_id')
    data['lead_time_mean'] = data['lead_time_mean'].fillna(lt_store_mean)
    data['lead_time_std'] = data['lead_time_std'].fillna(lt_store_std)

    # Safety stock calculation
    data['safety_stock'] = np.round(z * np.sqrt(data['lead_time_mean'] * np.square(data['demand_std'])
                                                + np.square(data['demand_mean']) * np.square(data['lead_time_std'])))
    data['reorder_point'] = np.round(data['lead_time_mean'] * data['demand_mean'] + data['safety_stock'])

    # Keep 30days stock by default
    data['order_upto_point'] = np.round(data['demand_mean'] * 30)

    # Adjustment for ethical
    data['order_upto_point'] = np.round(np.where(data['type'].isin(['ethical', 'high-value-ethical']),
                                                 data['order_upto_point'] * (1 / 2),
                                                 data['order_upto_point'] * (2 / 3)))

    # Sanity check, order_upto_point (max) to be not less than reorder point
    data['order_upto_point'] = np.round(np.where(data['order_upto_point'] < data['reorder_point'],
                                                 data['reorder_point'], data['order_upto_point']))

    # Where re-order point is 1,2,3 and is same as order_upto_point (max) then do max = max+1
    data['order_upto_point'] = np.round(np.where(((data['reorder_point'].isin([1, 2, 3])) &
                                                  (data['order_upto_point'] == data['reorder_point'])),
                                                 data['order_upto_point'] + 1, data['order_upto_point']))

    # order-upto-point 1,2,3 corrections
    # Source - ops/ipc/safety_stock
    one_index = data[
        data['order_upto_point'].isin([1])].index
    data.loc[one_index, 'safety_stock'] = 0
    data.loc[one_index, 'reorder_point'] = 1
    data.loc[one_index, 'order_upto_point'] = 2

    two_index = data[
        data['order_upto_point'].isin([2])].index
    data.loc[two_index, 'safety_stock'] = 0
    data.loc[two_index, 'reorder_point'] = 1
    data.loc[two_index, 'order_upto_point'] = 2

    three_index = data[
        data['order_upto_point'].isin([3])].index
    data.loc[three_index, 'safety_stock'] = 1
    data.loc[three_index, 'reorder_point'] = 2
    data.loc[three_index, 'order_upto_point'] = 3

    # Where re-order point is >=4 and is same as order_upto_point (max) then do max = 1.5*max
    data['order_upto_point'] = np.round(np.where(((data['reorder_point'] >= 4) &
                                                  (data['order_upto_point'] == data['reorder_point'])),
                                                 data['order_upto_point'] * 1.5, data['order_upto_point']))

    # Sanity check for max again
    data['order_upto_point'] = np.round(np.where(data['order_upto_point'] < data['reorder_point'],
                                                 data['reorder_point'], data['order_upto_point']))

    data = data.rename(columns={'safety_stock': 'min',
                                'reorder_point': 'safety_stock',
                                'order_upto_point': 'max'})

    data = data[['drug_id', 'min', 'safety_stock', 'max']]

    return data
