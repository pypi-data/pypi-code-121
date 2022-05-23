import pandas as pd
import numpy as np
import time
from scipy.stats import norm

from zeno_etl_libs.utils.ipc.data_prep import forecast_data_prep
from zeno_etl_libs.utils.ipc.item_classification import abc_xyz_classification
from zeno_etl_libs.utils.ipc.forecasting_modules.helper_functions import sum_std,\
    applyParallel, applyParallel_lstm
from zeno_etl_libs.utils.ipc.forecasting_modules.lstm import lstm_forecast
from zeno_etl_libs.utils.ipc.forecasting_modules.moving_average import moving_average
from zeno_etl_libs.utils.ipc.forecasting_modules.prophet import prophet_weekly_predict
from zeno_etl_libs.utils.ipc.lead_time import lead_time
from zeno_etl_libs.utils.ipc.safety_stock import safety_stock_calc


def ipc_forecast_reset(
    store_id, type_list, reset_date, corrections_flag,
    corrections_selling_probability_cutoff,
    corrections_cumulative_probability_cutoff, db, schema,
    drug_type_list_v4, v5_active_flag, v6_active_flag, v6_type_list,
    v6_ptr_cut_off, chronic_max_flag='N', logger=None):
    '''DATA PREPATION'''
    cal_drug_sales_weekly, cal_drug_sales_monthly,\
        cal_sales = forecast_data_prep(store_id, type_list, reset_date,
                                       db, schema, logger)

    '''ITEM CLASSIFICATION'''
    drug_class, bucket_sales = abc_xyz_classification(
        cal_drug_sales_monthly, logger)

    '''FORECASTING'''
    forecast_horizon = 4
    # LSTM
    week_in = 8
    week_out = 4
    epochs = 200
    n_neurons = 8
    use_dropout = 0.2
    error_factor = 2
    lstm_drug_list = drug_class.loc[
        (drug_class['bucket_abc'] == 'A') & (drug_class['bucket_xyz'] == 'X') |
        (drug_class['bucket_abc'] == 'A') & (drug_class['bucket_xyz'] == 'Y') |
        (drug_class['bucket_abc'] == 'B') & (drug_class['bucket_xyz'] == 'X'),
        'drug_id']
    lstm_data_weekly = cal_drug_sales_weekly.loc[
        cal_drug_sales_weekly['drug_id'].isin(lstm_drug_list)]
    start = time.time()
    lstm_weekly_fcst = applyParallel_lstm(
        lstm_data_weekly.groupby('drug_id'), lstm_forecast,
        n_neurons=n_neurons, week_in=week_in, week_out=week_out,
        forecast_horizon=forecast_horizon, epochs=epochs,
        use_dropout=use_dropout, error_factor=error_factor).\
        reset_index(drop=True)
    end = time.time()
    print('Run time ', end-start)

    # MOVING AVERAGES
    ma_drug_list = drug_class.loc[
        (drug_class['bucket_abc'] == 'B') & (drug_class['bucket_xyz'] == 'Y') |
        (drug_class['bucket_abc'] == 'B') & (drug_class['bucket_xyz'] == 'Z') |
        (drug_class['bucket_abc'] == 'C') & (drug_class['bucket_xyz'] == 'X'),
        'drug_id']
    ma_data_weekly = cal_drug_sales_weekly.loc[
        cal_drug_sales_weekly['drug_id'].isin(ma_drug_list)]
    start = time.time()
    ma_weekly_fcst = ma_data_weekly.groupby('drug_id').\
        apply(moving_average).reset_index(drop=True)
    end = time.time()
    print('Run time ', end-start)

    # PROPHET
    prophet_drug_list = drug_class.loc[
        (drug_class['bucket_abc'] == 'C') & (drug_class['bucket_xyz'] == 'Y') |
        (drug_class['bucket_abc'] == 'C') & (drug_class['bucket_xyz'] == 'Z') |
        (drug_class['bucket_abc'] == 'A') & (drug_class['bucket_xyz'] == 'Z'),
        'drug_id']
    prophet_data_weekly = cal_drug_sales_weekly.loc[
        cal_drug_sales_weekly['drug_id'].isin(prophet_drug_list)]
    start = time.time()
    prophet_weekly_fcst = applyParallel(
        prophet_data_weekly.groupby('drug_id'), prophet_weekly_predict).\
        reset_index(drop=True)
    end = time.time()
    print('Run time ', end-start)

    '''COMPILING OUTPUT AND PERCENTILE FORECAST'''
    columns = ['model', 'drug_id', 'date', 'fcst', 'std']

    ma_weekly_fcst['model'] = 'MA'
    ma_weekly_fcst = ma_weekly_fcst[columns]

    prophet_weekly_fcst['model'] = 'Prophet'
    prophet_weekly_fcst = prophet_weekly_fcst[columns]

    lstm_weekly_fcst['model'] = 'LSTM'
    lstm_weekly_fcst = lstm_weekly_fcst[columns]

    weekly_fcst = pd.concat(
        [ma_weekly_fcst, prophet_weekly_fcst, lstm_weekly_fcst], axis=0)
    percentile_bucket_dict = {
        'AX': 0.5, 'AY': 0.5, 'AZ': 0.5,
        'BX': 0.5, 'BY': 0.6, 'BZ': 0.6,
        'CX': 0.5, 'CY': 0.6, 'CZ': 0.6}

    print(weekly_fcst.drug_id.nunique())
    weekly_fcst = weekly_fcst.merge(
        drug_class[['drug_id', 'bucket_abc', 'bucket_xyz']],
        on='drug_id', how='inner')
    weekly_fcst['bucket'] = (
        weekly_fcst['bucket_abc'] + weekly_fcst['bucket_xyz'])
    weekly_fcst.drop(['bucket_abc', 'bucket_xyz'], axis=1, inplace=True)

    for key in percentile_bucket_dict.keys():
        print(key, percentile_bucket_dict[key])
        indexs = weekly_fcst[weekly_fcst.bucket == key].index
        weekly_fcst.loc[indexs, 'percentile'] = percentile_bucket_dict[key]
        weekly_fcst.loc[indexs, 'fcst'] = np.round(
            weekly_fcst.loc[indexs, 'fcst'] +
            norm.ppf(percentile_bucket_dict[key]) *
            weekly_fcst.loc[indexs, 'std'])

    agg_fcst = weekly_fcst.groupby(
        ['model', 'drug_id', 'bucket', 'percentile']).\
        agg({'fcst': 'sum', 'std': sum_std}).reset_index()

    '''LEAD TIME CALCULATION'''
    lt_drug, lt_store_mean, lt_store_std = lead_time(
        store_id, cal_sales, reset_date, db, schema, logger)

    '''SAFETY STOCK CALCULATION'''
    safety_stock_df, df_corrections, df_corrections_111, \
    drugs_max_to_lock_ipcv6, drug_rejects_ipcv6 = safety_stock_calc(
        agg_fcst, store_id, forecast_horizon, lt_drug,
        lt_store_mean, lt_store_std, reset_date, corrections_flag,
        corrections_selling_probability_cutoff,
        corrections_cumulative_probability_cutoff, chronic_max_flag,
        v5_active_flag, v6_active_flag, v6_type_list,
        v6_ptr_cut_off, drug_type_list_v4, db, schema, logger)

    return drug_class, weekly_fcst, safety_stock_df, df_corrections, \
           df_corrections_111, drugs_max_to_lock_ipcv6, drug_rejects_ipcv6
