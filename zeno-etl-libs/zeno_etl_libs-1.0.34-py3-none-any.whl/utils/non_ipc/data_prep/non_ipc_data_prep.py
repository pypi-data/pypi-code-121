'''
Author - vishal.gupta@generico.in
Objective - Data preparation main scripts for Non IPC stores
'''

import datetime
from zeno_etl_libs.utils.ipc.data_prep import forecast_data_prep
from zeno_etl_libs.utils.non_ipc.data_prep.patient_data import forecast_patient_data
from zeno_etl_libs.utils.ipc.item_classification import abc_xyz_classification


def non_ipc_data_prep(store_id_list, reset_date, type_list, db, schema,
                      agg_week_cnt=4, logger=None):

    # getting demand data
    cal_drug_sales_weekly, _, _ = forecast_data_prep(
        store_id_list, type_list, reset_date, db, schema)

    # getting patient data
    cal_drug_patient_weekly = forecast_patient_data(
        store_id_list, type_list, reset_date, db, schema)

    # merging patient and demand data
    cal_drug_data_weekly = cal_drug_sales_weekly.merge(cal_drug_patient_weekly)

    '''ADDITIONAL CHECKS'''
    n = 12
    prev_n_week_dt = (
        cal_drug_data_weekly['date'].max() - datetime.timedelta(n*7))
    logger.info('Previous week date for last 12 weeks' + str(prev_n_week_dt))
    prev_n_week_sales = cal_drug_data_weekly[
        cal_drug_data_weekly['date'] > prev_n_week_dt].\
        groupby('drug_id')['net_sales_quantity'].sum().reset_index()
    prev_no_sales_drug_weekly = prev_n_week_sales.loc[
        prev_n_week_sales['net_sales_quantity'] <= 0, 'drug_id'].values
    prev_sales_drug_weekly = prev_n_week_sales.loc[
        prev_n_week_sales['net_sales_quantity'] > 0, 'drug_id'].values
    logger.info('No net sales of drugs within last 12 weeks' +
                str(len(prev_no_sales_drug_weekly)))
    logger.info('Sales of drugs within last 12 weeks' +
                str(len(prev_sales_drug_weekly)))

    # getting drug id with atleast one sale in last 12 weeks
    cal_drug_data_weekly = cal_drug_data_weekly[
        cal_drug_data_weekly.drug_id.isin(prev_sales_drug_weekly)]

    '''4 WEEKS AGGREGATION'''
    cal_drug_data_weekly['week_number'] = cal_drug_data_weekly.\
        groupby('drug_id')['date'].rank(ascending=False) - 1
    cal_drug_data_weekly['agg_wk_count'] = (
        cal_drug_data_weekly['week_number']/agg_week_cnt).astype(int) + 1

    agg_wk_ct_lt_4 = cal_drug_data_weekly.\
        groupby('agg_wk_count')['week_number'].nunique().reset_index()
    agg_wk_ct_lt_4 = agg_wk_ct_lt_4.query('week_number < 4')['agg_wk_count']

    # removing incomplete 4-week period
    cal_drug_data_weekly = cal_drug_data_weekly[
        ~cal_drug_data_weekly['agg_wk_count'].isin(agg_wk_ct_lt_4)]

    cal_drug_data_agg_weekly = cal_drug_data_weekly.\
        groupby(['drug_id', 'agg_wk_count']).\
        agg({'date': 'min', 'net_sales_quantity': 'sum', 'patient_count': 'sum'
             }).\
        reset_index()
    cal_drug_data_agg_weekly.sort_values(['drug_id', 'date'], inplace=True)

    '''SKU CLASSIFICATIONS'''
    # Taking latest 3 4-week period for classification
    bucket_period = 3
    agg_wk_classification = cal_drug_data_agg_weekly.loc[
        cal_drug_data_agg_weekly['agg_wk_count'] <= bucket_period, 'date'
    ].dt.date.unique()
    cal_drug_data_classification = cal_drug_data_agg_weekly[
        cal_drug_data_agg_weekly['date'].isin(agg_wk_classification)]
    cal_drug_data_classification.rename(
        columns={'date': 'month_begin_dt'}, inplace=True)

    drug_class, bucket_sales = abc_xyz_classification(
        cal_drug_data_classification)

    return cal_drug_data_agg_weekly, cal_drug_data_weekly, drug_class,\
        bucket_sales
