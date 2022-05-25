'''
Author - vishal.gupta@generico.in
Objective -  Safety stock calculations for non-ipc old stores
'''

import numpy as np
import pandas as pd

from datetime import datetime
from scipy.stats import norm
from zeno_etl_libs.utils.ipc.lead_time import lead_time

from zeno_etl_libs.utils.ipc.heuristics.ipcv4_heuristics import ipcv4_heuristics
from zeno_etl_libs.utils.ipc.heuristics.ipcv5_heuristics import v5_corrections
# from zeno_etl_libs.utils.ipc.heuristics.ipcv6_heuristics import v6_corrections


def non_ipc_safety_stock_calc(
    store_id, cal_sales, reset_date, final_predict, drug_class,
    corrections_flag, corrections_selling_probability_cutoff,
    corrections_cumulative_probability_cutoff, chronic_max_flag,
    train_flag, drug_type_list_v4, v5_active_flag, v6_active_flag,
    v6_type_list, v6_ptr_cut_off, db, schema, logger):

    '''LEAD TIME CALCULATION'''
    lt_drug, lt_store_mean, lt_store_std = lead_time(
        store_id, cal_sales, reset_date, db, schema, logger)

    service_level = 0.95
    num_days = 4 * 7
    order_freq = 4
    z = norm.ppf(service_level)
    print(lt_store_mean, lt_store_std)

    drug_class = drug_class.copy()
    drug_class['bucket'] = drug_class['bucket_abc'] + drug_class['bucket_xyz']

    safety_stock_df = final_predict.merge(
        lt_drug[['drug_id', 'lead_time_mean', 'lead_time_std']],
        how='left', on='drug_id')
    safety_stock_df['lead_time_mean'].fillna(lt_store_mean, inplace=True)
    safety_stock_df['lead_time_std'].fillna(lt_store_std, inplace=True)

    safety_stock_df = safety_stock_df.merge(
        drug_class[['drug_id', 'bucket']], on='drug_id', how='left')
    safety_stock_df['bucket'].fillna('NA', inplace=True)
    safety_stock_df['demand_daily'] = safety_stock_df['fcst']/num_days
    safety_stock_df['demand_daily_deviation'] = (
        safety_stock_df['std']/np.sqrt(num_days))

    # heuristics #1
    safety_stock_df['lead_time_std'] = np.where(
        safety_stock_df['lead_time_std'] < 1,
        lt_store_std, safety_stock_df['lead_time_std'])

    # non ipc store safety stock
    safety_stock_df['safety_stock'] = np.round(
        z * np.sqrt(
            (
                safety_stock_df['lead_time_mean'] *
                safety_stock_df['demand_daily_deviation'] *
                safety_stock_df['demand_daily_deviation']
            ) +
            (
                safety_stock_df['lead_time_std'] *
                safety_stock_df['lead_time_std'] *
                safety_stock_df['demand_daily'] *
                safety_stock_df['demand_daily']
            )))
    safety_stock_df['reorder_point'] = np.round(
        safety_stock_df['safety_stock'] +
        safety_stock_df['demand_daily'] * safety_stock_df['lead_time_mean'])
    safety_stock_df['order_upto_point'] = np.round(
        safety_stock_df['reorder_point'] +
        safety_stock_df['demand_daily'] * order_freq)

    safety_stock_df['safety_stock_days'] = np.round(
        num_days * safety_stock_df['safety_stock'] /
        safety_stock_df['fcst'])
    safety_stock_df['reorder_days'] = np.round(
        num_days * safety_stock_df['reorder_point'] /
        safety_stock_df['fcst'])
    safety_stock_df['order_upto_days'] = np.round(
        num_days * safety_stock_df['order_upto_point'] /
        safety_stock_df['fcst'])
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

    safety_stock_df = safety_stock_df.merge(fptr, on='drug_id', how='left')
    safety_stock_df['fptr'].fillna(100, inplace=True)
    safety_stock_df['max_value'] = (
        safety_stock_df['fptr'] * safety_stock_df['order_upto_point'])

    # correction plugin - Start
    if corrections_flag & train_flag:
        safety_stock_df['correction_flag'] = 'N'
        safety_stock_df['store_id'] = store_id
        print("corrections code is running now:")

        q_prob = f"""select * from "{schema}"."ipc-corrections-rest-cases" """
        q_prob_111 = f"""select * from "{schema}"."ipc-corrections-111-cases" """
        prob_matrix = db.get_df(q_prob)
        df_111 = db.get_df(q_prob_111)
        prob_matrix.columns = [c.replace('-', '_') for c in prob_matrix.columns]
        df_111.columns = [c.replace('-', '_') for c in df_111.columns]

        # list of drugs for which corrections is required. i.e. max value 0.
        df_corrections_list = safety_stock_df[
            safety_stock_df['order_upto_point'] == 0][['store_id', 'drug_id']]
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
            safety_stock_df[['store_id', 'drug_id', 'curr_inventory']],
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
        safety_stock_df = safety_stock_df.set_index(['store_id', 'drug_id'])

        safety_stock_df.update(df_corrections)
        safety_stock_df = safety_stock_df.reset_index()
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
            safety_stock_df[['store_id', 'drug_id', 'curr_inventory']],
            on=['store_id', 'drug_id'], how='left', validate='one_to_one')

        df_corrections_111 = df_corrections_111.set_index(
            ['store_id', 'drug_id'])
        safety_stock_df = safety_stock_df.set_index(['store_id', 'drug_id'])
        safety_stock_df.update(df_corrections_111)

        safety_stock_df = safety_stock_df.reset_index()
        df_corrections_111 = df_corrections_111.reset_index()

        # set reset date
        curr_date = str(datetime.now())
        df_corrections['reset_date'] = curr_date
        df_corrections_111['reset_date'] = curr_date
        safety_stock_df = safety_stock_df.drop(['store_id'], axis=1)

    else:
        print('corrections block skipped :')
        df_corrections = pd.DataFrame()
        df_corrections_111 = pd.DataFrame()
        safety_stock_df['correction_flag'] = 'N'

    # Correction plugin - End #

    # Chronic drug changes
    if chronic_max_flag == 'Y':
        # based on ME OOS feedback - keep chronic drugs
        drug_max_zero = tuple(
            safety_stock_df.query('order_upto_point == 0')['drug_id'])

        # reading chronic drug list
        drug_chronic_max_zero_query = '''
                select id as drug_id from "{schema}".drugs
                where category = 'chronic'
                and id in {0}
                '''.format(str(drug_max_zero), schema=schema)
        drug_chronic_max_zero = db.get_df(drug_chronic_max_zero_query)[
            'drug_id']

        # setting non zero max for such drugs
        safety_stock_df.loc[
            (safety_stock_df['drug_id'].isin(drug_chronic_max_zero)) &
            (safety_stock_df['order_upto_point'] == 0),
            'order_upto_point'] = 1
        safety_stock_df.loc[
            (safety_stock_df['drug_id'].isin(drug_chronic_max_zero)) &
            (safety_stock_df['order_upto_point'] == 0),
            'correction_flag'] = 'Y_chronic'

    safety_stock_df = ipcv4_heuristics(safety_stock_df, drug_type_list_v4,
                                       db, schema)

    if v5_active_flag == "Y":
        logger.info("IPC V5 Correction Starts")
        safety_stock_df = v5_corrections(store_id, safety_stock_df,
                                         db, schema, logger)
        logger.info("IPC V5 Correction Successful")

    # if v6_active_flag == "Y":
    #     logger.info("IPC V6 Correction Starts")
    #     safety_stock_df, drugs_max_to_lock_ipcv6, drug_rejects_ipcv6 = \
    #         v6_corrections(store_id, safety_stock_df, reset_date, v6_type_list,
    #                v6_ptr_cut_off, logger)
    #
    #     # add algo name to v6 write table
    #     drugs_max_to_lock_ipcv6["algo"] = 'non-ipc'
    #     drug_rejects_ipcv6["algo"] = 'non-ipc'
    #     logger.info("IPC V6 Correction Successful")
    # else:
    drugs_max_to_lock_ipcv6 = pd.DataFrame()
    drug_rejects_ipcv6 = pd.DataFrame()

    return safety_stock_df, df_corrections, df_corrections_111, \
           drugs_max_to_lock_ipcv6, drug_rejects_ipcv6
