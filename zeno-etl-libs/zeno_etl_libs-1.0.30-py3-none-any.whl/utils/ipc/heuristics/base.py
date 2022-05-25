'''
Base heuristics - use the last 4 weeks data to adjust the safety stock numbers
Conditions -
a. Applies for A/B only
b. recency adjustment factor = order upto point/ last 4 weeks sales
c. No changes when RAF: {0.25, 0.75}
d. If not then then do adjustment to bring it to 0.25 or 0.75
'''

import numpy as np
from datetime import datetime, timedelta


def get_demand_heuristics(start_date, end_date, drug_list, store_id,
                          db, schema, logger):
    # sales query
    print('getting data for store', store_id)
    sales_query = f"""
            select date("created-at") as "sales-date", "drug-id" , 
                    sum("net-quantity") as "net-sales-quantity"
            from "{schema}".sales s
            where "store-id" = {store_id}
            and date("created-at") >= '{start_date}'
            and date("created-at") < '{end_date}'
            and "drug-id" in {drug_list}
            group by "sales-date", "drug-id"
            """
    sales_history = db.get_df(sales_query)
    sales_history.columns = [c.replace('-', '_') for c in sales_history.columns]

    # cfr pr loss
    cfr_pr_query = f"""
            select "attributed-loss-date", "drug-id",
            sum("loss-quantity") as "loss-quantity"
            from "{schema}"."cfr-patient-request"
            where "shortbook-date" >= '{start_date}'
            and "shortbook-date" < '{end_date}'
            and "drug-id" <> -1
            and ("drug-category" = 'chronic' or "repeatability-index" >= 40)
            and "loss-quantity" > 0
            and "drug-id" in {drug_list}
            and "store-id" = {store_id}
            group by  "attributed-loss-date", "drug-id"
            """
    cfr_pr = db.get_df(cfr_pr_query)
    cfr_pr["loss-quantity"] = cfr_pr["loss-quantity"].astype(float)
    cfr_pr.columns = [c.replace('-', '_') for c in cfr_pr.columns]

    # total demand merge
    demand = sales_history.merge(
        cfr_pr, left_on=['sales_date', 'drug_id'],
        right_on=['attributed_loss_date', 'drug_id'], how='left')
    demand['sales_date'] = demand['sales_date'].combine_first(
        demand['attributed_loss_date'])
    demand['net_sales_quantity'].fillna(0, inplace=True)
    demand['loss_quantity'].fillna(0, inplace=True)
    demand['net_sales_quantity'] += demand['loss_quantity']
    demand.drop(
        ['attributed_loss_date', 'loss_quantity'], axis=1, inplace=True)

    # aggregating demand at level
    demand_agg = demand.groupby(
        ['drug_id'])['net_sales_quantity'].sum().reset_index()
    demand_agg.columns = ['drug_id', 'historical_demand']

    # getting drug type
    drug_type_query = """
            select id as drug_id, type as drug_type 
            from "{schema}".drugs 
            where id in {0}
            """.format(drug_list, schema=schema)
    drug_type = db.get_df(drug_type_query)

    demand_agg = demand_agg.merge(drug_type, on=['drug_id'], how='left')

    return demand_agg


def base_heuristics(
    store_id, safety_stock_df, reset_date, db, schema, logger=None,
        raf_range=(0.25, 0.75), corr_raf=0.5):
    # getting time period for last 4 weeks
    date = datetime.strptime(reset_date, '%Y-%m-%d')
    end_date = (date - timedelta(days=date.weekday())).date()
    start_date = end_date - timedelta(days=28)
    end_date = str(end_date)
    start_date = str(start_date)
    logger.info(
        'Getting last 4 week data for base heuristic from' + start_date +
        'to' + end_date)

    # getting demand for heuristics - A/B class only
    bucket_class_list = ['AX', 'AY', 'AZ', 'BX', 'BY', 'BZ']
    drug_list = tuple(list(safety_stock_df.loc[
        safety_stock_df.bucket.isin(bucket_class_list),
        'drug_id']))
    demand = get_demand_heuristics(
        start_date, end_date, drug_list, store_id, db, schema, logger)
    safety_stock_adj = safety_stock_df.merge(
        demand, how='left', on=['drug_id'])
    safety_stock_adj['historical_demand'].fillna(0, inplace=True)

    # RAF factor calculation
    safety_stock_adj['raf'] = np.select(
        [safety_stock_adj['historical_demand'] == 0],
        [0.5],
        default=safety_stock_adj['order_upto_point'] /
        safety_stock_adj['historical_demand'])

    # adjustment using RAF: for low
    low_raf_index = safety_stock_adj[
        (safety_stock_adj['bucket'].isin(bucket_class_list)) &
        (safety_stock_adj['raf'] < raf_range[0])
    ].index
    safety_stock_adj.loc[low_raf_index, 'order_upto_point'] = np.round(
        np.where(
            safety_stock_adj.loc[low_raf_index, 'order_upto_point'] == 0,
            safety_stock_adj.loc[low_raf_index, 'historical_demand']*corr_raf,
            (safety_stock_adj.loc[low_raf_index, 'order_upto_point']*corr_raf /
             safety_stock_adj.loc[low_raf_index, 'raf'])
        ))
    safety_stock_adj.loc[low_raf_index, 'reorder_point'] = np.round(
        safety_stock_adj.loc[low_raf_index, 'order_upto_point']/2)
    safety_stock_adj.loc[low_raf_index, 'safety_stock'] = np.round(
        safety_stock_adj.loc[low_raf_index, 'reorder_point']/2)
    #     print(safety_stock_adj.head())

    # adjustment using RAF: for high
    high_raf_index = safety_stock_adj[
        (safety_stock_adj['bucket'].isin(bucket_class_list)) &
        (safety_stock_adj['raf'] > raf_range[1])
    ].index
    safety_stock_adj.loc[high_raf_index, 'order_upto_point'] = np.round(
        safety_stock_adj.loc[high_raf_index, 'order_upto_point'] *
        corr_raf / safety_stock_adj['raf'])
    safety_stock_adj.loc[high_raf_index, 'reorder_point'] = np.round(
        safety_stock_adj.loc[high_raf_index, 'order_upto_point']/2)
    safety_stock_adj.loc[high_raf_index, 'safety_stock'] = np.round(
        safety_stock_adj.loc[high_raf_index, 'reorder_point']/2)
    logger.info(
        'Out of total line items ' + str(len(safety_stock_adj)) + '\n' +
        'Decreased: Total ' + str(len(high_raf_index)) + '\n' +
        'Decreased: Generic ' +
        str(len(safety_stock_adj.iloc[high_raf_index].
            query('drug_type == "generic"'))) + '\n' +
        'Decreased: Ethical ' +
        str(len(safety_stock_adj.iloc[high_raf_index].
            query('drug_type == "ethical"'))) + '\n' +
        'Increased: Total ' + str(len(low_raf_index)) + '\n' +
        'Increased: Generic ' +
        str(len(safety_stock_adj.iloc[low_raf_index].
            query('drug_type == "generic"'))) + '\n' +
        'Increased: Ethical ' +
        str(len(safety_stock_adj.iloc[low_raf_index].
            query('drug_type == "ethical"')))
          )

    return safety_stock_adj[safety_stock_df.columns]
