import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
from zeno_etl_libs.utils.ipc.heuristics.base import base_heuristics
from zeno_etl_libs.utils.ipc.heuristics.ipcv4_heuristics import ipcv4_heuristics
from zeno_etl_libs.utils.ipc.heuristics.ipcv5_heuristics import v5_corrections
# from scripts.ops.ipc.heuristics.ipcv6_heuristics import v6_corrections

'''
service level - 95%
safety stock = z-score * sqrt(std_lead_time^2 * avg_demand^2 +
                              avg_lead_time^2 * std_demand^2)
re-order point = avg_lead_time + avg_demand + safety stock
'''


def safety_stock_calc(agg_fcst, store_id, forecast_horizon, lt_drug,
                      lt_store_mean, lt_store_std, reset_date,
                      corrections_flag,
                      corrections_selling_probability_cutoff,
                      corrections_cumulative_probability_cutoff,
                      chronic_max_flag, v5_active_flag, v6_active_flag,
                      v6_type_list, v6_ptr_cut_off,
                      drug_type_list_v4, db, schema, logger):
    service_level = 0.95
    fcst_weeks = 4
    order_freq = 4
    z = norm.ppf(service_level)
    print(lt_store_mean, lt_store_std)

    safety_stock_df = agg_fcst.merge(
        lt_drug[['drug_id', 'lead_time_mean', 'lead_time_std']],
        how='left', on='drug_id')
    safety_stock_df['lead_time_mean'].fillna(lt_store_mean, inplace=True)
    safety_stock_df['lead_time_std'].fillna(lt_store_std, inplace=True)
    # heuristics #1
    safety_stock_df['lead_time_std'] = np.where(
        safety_stock_df['lead_time_std'] < 1,
        lt_store_std, safety_stock_df['lead_time_std'])

    # safeyty stock value - variation in demand & lead time
    safety_stock_df['safety_stock'] = safety_stock_df.apply(
        lambda row: np.round(z * np.sqrt(
            (row['lead_time_mean'] * np.square(
                row['std'] / np.sqrt(fcst_weeks * 7)) +
             np.square(row['lead_time_std'] * row['fcst'] / fcst_weeks / 7))
        )), axis=1)
    safety_stock_df['safety_stock'] = np.where(
        safety_stock_df['fcst'] == 0, 0, safety_stock_df['safety_stock'])

    # consider avg fulfillment times
    safety_stock_df['reorder_point'] = safety_stock_df.apply(
        lambda row: np.round(
            row['lead_time_mean'] * row['fcst'] / fcst_weeks / 7),
        axis=1) + safety_stock_df['safety_stock']

    # ordering frequency 7 days
    # heuristics #2
    safety_stock_df['order_upto_point'] = (
            safety_stock_df['reorder_point'] +
            np.round(
                np.where(
                    # if rounding off give 0, increase it to 4-week forecast
                    (safety_stock_df['reorder_point'] +
                     safety_stock_df[
                         'fcst'] * order_freq / fcst_weeks / 7 < 0.5) &
                    (safety_stock_df['fcst'] > 0),
                    safety_stock_df['fcst'],
                    safety_stock_df['fcst'] * order_freq / fcst_weeks / 7))
    )

    # correction for negative forecast
    safety_stock_df['safety_stock'] = np.where(
        safety_stock_df['safety_stock'] < 0,
        0, safety_stock_df['safety_stock'])
    safety_stock_df['reorder_point'] = np.where(
        safety_stock_df['reorder_point'] < 0,
        0, safety_stock_df['reorder_point'])
    safety_stock_df['order_upto_point'] = np.where(
        safety_stock_df['order_upto_point'] < 0,
        0, safety_stock_df['order_upto_point'])

    safety_stock_df['safety_stock_days'] = np.round(
        7 * forecast_horizon * safety_stock_df['safety_stock'] /
        safety_stock_df['fcst'])
    safety_stock_df['reorder_days'] = np.round(
        7 * forecast_horizon * safety_stock_df['reorder_point'] /
        safety_stock_df['fcst'])
    safety_stock_df['order_upto_days'] = np.round(
        7 * forecast_horizon * safety_stock_df['order_upto_point'] /
        safety_stock_df['fcst'])

    # heuristics #3
    safety_stock_df['order_upto_point'] = np.where(
        safety_stock_df['order_upto_days'] < 14,
        np.round(14 * safety_stock_df['fcst'] / fcst_weeks / 7),
        safety_stock_df['order_upto_point']
    )
    safety_stock_df['order_upto_days'] = np.round(
        7 * forecast_horizon * safety_stock_df['order_upto_point'] /
        safety_stock_df['fcst'])

    # recent actuals base adjustments
    safety_stock_df = base_heuristics(
        store_id, safety_stock_df, reset_date, db, schema, logger)

    # getting order value
    drug_list = list(safety_stock_df['drug_id'].unique())
    print(len(drug_list))
    drug_str = str(drug_list).replace('[', '(').replace(']', ')')

    fptr_query = """
        select "drug-id" , avg(ptr) as fptr, sum(quantity) as curr_inventory
        from "{schema}"."inventory-1" i 
        where "store-id" = {store_id}
        and "drug-id" in {drug_str}
        group by "drug-id" 
        """.format(store_id=store_id, drug_str=drug_str, schema=schema)
    fptr = db.get_df(fptr_query)
    fptr.columns = [c.replace('-', '_') for c in fptr.columns]
    fptr["fptr"] = fptr["fptr"].astype(float)

    final_pred_ss_df = safety_stock_df.merge(fptr, on='drug_id', how='left')
    final_pred_ss_df['fptr'].fillna(100, inplace=True)
    final_pred_ss_df['max_value'] = (
            final_pred_ss_df['fptr'] * final_pred_ss_df['order_upto_point'])

    print(final_pred_ss_df.groupby('bucket')['max_value'].sum().reset_index())
    print(28 * final_pred_ss_df['order_upto_point'].sum() /
          final_pred_ss_df['fcst'].sum())
    print(final_pred_ss_df['max_value'].sum())

    # correction plugin - Start
    if corrections_flag:
        final_pred_ss_df['correction_flag'] = 'N'
        final_pred_ss_df['store_id'] = store_id
        print("corrections code is running now:")

        q_prob = f"""select * from "{schema}"."ipc-corrections-rest-cases" """
        q_prob_111 = f"""select * from "{schema}"."ipc-corrections-111-cases" """
        prob_matrix = db.get_df(q_prob)
        df_111 = db.get_df(q_prob_111)
        prob_matrix.columns = [c.replace('-', '_') for c in prob_matrix.columns]
        df_111.columns = [c.replace('-', '_') for c in df_111.columns]

        # list of drugs for which corrections is required. i.e. max value 0.
        df_corrections_list = final_pred_ss_df[
            final_pred_ss_df['order_upto_point'] == 0][['store_id', 'drug_id']]
        df_corrections = pd.merge(
            df_corrections_list, prob_matrix, how='inner',
            on=['store_id', 'drug_id'], validate='one_to_one')

        df_corrections = df_corrections.drop(columns={'corrected_max'})
        df_corrections['order_upto_point'] = np.round(
            df_corrections['current_ma_3_months'])

        df_corrections_1 = df_corrections[
            (df_corrections['cumm_prob'] >=
             corrections_cumulative_probability_cutoff['ma_less_than_2']) &
            (df_corrections['current_flag_ma_less_than_2'] == 1)]
        df_corrections_2 = df_corrections[
            (df_corrections['cumm_prob'] >=
             corrections_cumulative_probability_cutoff['ma_more_than_2']) &
            (df_corrections['current_flag_ma_less_than_2'] == 0)]

        df_corrections_1 = df_corrections_1[
            (df_corrections_1['selling_probability'] >=
             corrections_selling_probability_cutoff['ma_less_than_2']) &
            (df_corrections_1['current_flag_ma_less_than_2'] == 1)]
        df_corrections_2 = df_corrections_2[
            (df_corrections_2['selling_probability'] >=
             corrections_selling_probability_cutoff['ma_more_than_2']) &
            (df_corrections_2['current_flag_ma_less_than_2'] == 0)]

        df_corrections = pd.concat(
            [df_corrections_1, df_corrections_2]).reset_index(drop=True)
        df_corrections_final = df_corrections.copy()[
            ['store_id', 'drug_id', 'current_bucket', 'selling_probability',
             'cumm_prob', 'current_flag_ma_less_than_2',
             'avg_ptr', 'current_ma_3_months']]

        # adding run time current inventory
        df_corrections_final = pd.merge(
            df_corrections_final,
            final_pred_ss_df[['store_id', 'drug_id', 'curr_inventory']],
            on=['store_id', 'drug_id'], how='left', validate='one_to_one')

        df_corrections = df_corrections[
            ['store_id', 'drug_id', 'order_upto_point']]
        df_corrections['reorder_point'] = np.floor(
            df_corrections['order_upto_point'] / 2)
        df_corrections['safety_stock'] = np.floor(
            df_corrections['order_upto_point'] / 4)

        df_corrections['correction_flag'] = 'Y'
        df_corrections['is_ipc'] = 'Y'

        df_corrections = df_corrections.set_index(['store_id', 'drug_id'])
        final_pred_ss_df = final_pred_ss_df.set_index(['store_id', 'drug_id'])

        final_pred_ss_df.update(df_corrections)
        final_pred_ss_df = final_pred_ss_df.reset_index()
        df_corrections = df_corrections.reset_index()

        df_corrections = pd.merge(
            df_corrections, df_corrections_final, on=['store_id', 'drug_id'],
            how='left', validate='one_to_one')

        # update 111 cases here.
        df_corrections_111 = pd.merge(
            df_corrections_list, df_111, how='inner',
            on=['store_id', 'drug_id'], validate='one_to_one')

        df_corrections_111 = df_corrections_111.drop(
            columns={'current_inventory', 'original_max', 'corrected_max',
                     'inv_impact', 'max_impact'}, axis=1)

        df_corrections_111['order_upto_point'] = np.round(
            df_corrections_111['ma_3_months'])
        df_corrections_111['reorder_point'] = np.floor(
            df_corrections_111['order_upto_point'] / 2)
        df_corrections_111['safety_stock'] = np.floor(
            df_corrections_111['order_upto_point'] / 4)

        df_corrections_111['correction_flag'] = 'Y'
        df_corrections_111['is_ipc'] = 'Y'

        # adding run time current inventory
        df_corrections_111 = pd.merge(
            df_corrections_111,
            final_pred_ss_df[['store_id', 'drug_id', 'curr_inventory']],
            on=['store_id', 'drug_id'], how='left', validate='one_to_one')

        df_corrections_111 = df_corrections_111.set_index(
            ['store_id', 'drug_id'])
        final_pred_ss_df = final_pred_ss_df.set_index(['store_id', 'drug_id'])
        final_pred_ss_df.update(df_corrections_111)

        final_pred_ss_df = final_pred_ss_df.reset_index()
        df_corrections_111 = df_corrections_111.reset_index()

        # set reset date
        curr_date = str(datetime.now())
        df_corrections['reset_date'] = curr_date
        df_corrections_111['reset_date'] = curr_date

    else:
        print('corrections block skipped :')
        final_pred_ss_df["store_id"] = store_id
        final_pred_ss_df["correction_flag"] = 'N'
        df_corrections = pd.DataFrame()
        df_corrections_111 = pd.DataFrame()

    # Correction plugin - End #
    final_pred_ss_df = final_pred_ss_df.drop(['store_id'], axis=1)

    # Chronic drug changes
    if chronic_max_flag == 'Y':
        # based on ME OOS feedback - keep chronic drugs
        drug_max_zero = tuple(
            final_pred_ss_df.query('order_upto_point == 0')['drug_id'])

        # reading chronic drug list
        drug_chronic_max_zero_query = '''
        select id as drug_id from "{schema}".drugs
        where category = 'chronic'
        and id in {0}
        '''.format(str(drug_max_zero), schema=schema)
        drug_chronic_max_zero = db.get_df(drug_chronic_max_zero_query)['drug_id']

        # setting non zero max for such drugs
        final_pred_ss_df.loc[
            (final_pred_ss_df['drug_id'].isin(drug_chronic_max_zero)) &
            (final_pred_ss_df['order_upto_point'] == 0),
            'order_upto_point'] = 1
        final_pred_ss_df.loc[
            (final_pred_ss_df['drug_id'].isin(drug_chronic_max_zero)) &
            (final_pred_ss_df['order_upto_point'] == 0),
            'correction_flag'] = 'Y_chronic'

    # Min/SS/Max overlap correction

    final_pred_ss_df['safety_stock_days'].fillna(0, inplace=True)
    final_pred_ss_df['reorder_days'].fillna(0, inplace=True)
    final_pred_ss_df['order_upto_days'].fillna(0, inplace=True)

    final_pred_ss_df = ipcv4_heuristics(final_pred_ss_df, drug_type_list_v4, db, schema)

    if v5_active_flag == "Y":
        logger.info("IPC V5 Correction Starts")
        final_pred_ss_df = v5_corrections(store_id, final_pred_ss_df, logger)
        logger.info("IPC V5 Correction Successful")

    # if v6_active_flag == "Y":
    #     logger.info("IPC V6 Correction Starts")
    #     final_pred_ss_df, drugs_max_to_lock_ipcv6, drug_rejects_ipcv6 = \
    #         v6_corrections(store_id, final_pred_ss_df, reset_date, v6_type_list,
    #                        v6_ptr_cut_off, logger)
    #
    #     # add algo name to v6 write table
    #     drugs_max_to_lock_ipcv6["algo"] = 'ipc'
    #     drug_rejects_ipcv6["algo"] = 'ipc'
    #     logger.info("IPC V6 Correction Successful")
    # else:
    drugs_max_to_lock_ipcv6 = pd.DataFrame()
    drug_rejects_ipcv6 = pd.DataFrame()

    return final_pred_ss_df, df_corrections, df_corrections_111, \
           drugs_max_to_lock_ipcv6, drug_rejects_ipcv6
