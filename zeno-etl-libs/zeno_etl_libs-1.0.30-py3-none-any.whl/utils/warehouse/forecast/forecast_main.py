"""
Author - vivek.sidagam@zeno.health
Objective - Forecastin module - different buckets different models
"""

import time
import pandas as pd
import numpy as np
from itertools import product

from zeno_etl_libs.utils.warehouse.forecast.errors import train_error, \
    train_error_ets_h1
from zeno_etl_libs.utils.warehouse.forecast.moving_average import \
    ma_train_monthly, \
    ma_predict_monthly
from zeno_etl_libs.utils.warehouse.forecast.ets import ets_train_monthly, \
    ets_predict_monthly
# from zeno_etl_libs.utils.warehouse.forecast.prophet import prophet_train_monthly,\
#     prophet_predict_monthly
from zeno_etl_libs.utils.warehouse.forecast.naive import naive_predict_monthly
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import \
    apply_parallel_ets


# from scripts.ops.warehouse.forecast.\
#     helper_functions import apply_parallel_prophet


def wh_forecast(drug_sales_monthly, wh_drug_list, drug_history, logger=None):
    """
    Bucketing based on History
    1. For drugs with history < 3 months -> Naive
    2. For drugs with history 3-11 month -> MA, SES
    3. For drugs with history >= 12 months -> MA, ETS
    """

    # BUCKET BASED ON HISTORY
    bucket_h3 = drug_history[drug_history['month_history'] < 3]
    bucket_h2minus = drug_history[
        (drug_history['month_history'] >= 3) &
        (drug_history['month_history'] <= 5)]
    bucket_h2 = drug_history[
        (drug_history['month_history'] >= 6) &
        (drug_history['month_history'] < 12)]
    bucket_h1 = drug_history[drug_history['month_history'] >= 12]
    bucket_log = '''
    Bucket H1 12+ months history - {},
    Bucket H2 6-11 months history - {},
    Bucket H2- 3-5 months history - {},
    Bucket H3 <3 months history - {}'''.format(
        len(bucket_h1), len(bucket_h2), len(bucket_h2minus), len(bucket_h3)
    )
    logger.info(bucket_log)

    # SUBSETTING SALE HISTORY DATA FOR BUCKETS
    drug_sales_monthly_bucket_h1 = drug_sales_monthly[
        drug_sales_monthly['drug_id'].isin(bucket_h1['drug_id'])]
    drug_sales_monthly_bucket_h2 = drug_sales_monthly[
        drug_sales_monthly['drug_id'].isin(bucket_h2['drug_id'])]
    drug_sales_monthly_bucket_h2minus = drug_sales_monthly[
        drug_sales_monthly['drug_id'].isin(bucket_h2minus['drug_id'])]
    drug_sales_monthly_bucket_h3 = drug_sales_monthly[
        drug_sales_monthly['drug_id'].isin(bucket_h3['drug_id'])]

    ''' H1 bucket - Train and Forecast'''
    logger.info(
        'Drugs for training' +
        str(drug_sales_monthly_bucket_h1.drug_id.nunique()))

    # FORECASTING MODULES: MOVING AVERAGES K=3

    ma_train_data_h1 = drug_sales_monthly_bucket_h1.copy()
    ma_train_data_h1 = ma_train_data_h1[
        ['drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # model parameters
    # k = 3  # N moving average
    horizon = 3  # future forecast

    # train
    start = time.time()
    ma_train_h1 = ma_train_data_h1.groupby('drug_id').apply(ma_train_monthly). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H1 MA Train: Run time ' + str(round(end - start, 2)) + 'secs')
    # train error
    start = time.time()
    ma_train_error_h1 = ma_train_h1.groupby('drug_id').apply(train_error). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H1 MA Error: Run time ' + str(round(end - start, 2)) + 'secs')
    # predict
    start = time.time()
    ma_predict_h1 = ma_train_data_h1.groupby('drug_id'). \
        apply(ma_predict_monthly).reset_index(drop=True)
    end = time.time()
    logger.info('H1 MA Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    # FORECASTING MODULES: EXPONENTIAL SMOOTHING

    ets_train_data_h1 = drug_sales_monthly_bucket_h1.copy()
    ets_train_data_h1 = ets_train_data_h1[
        ['drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # model parameters
    horizon = 3  # future forecast
    out_of_sample = 3  # out of sample forecast
    # holts winter implementation
    trend = ['additive', None]
    seasonal = ['additive', None]
    damped = [True, False]
    seasonal_periods = [12]
    use_boxcox = [True, False]
    ets_params = list(
        product(trend, seasonal, damped, seasonal_periods, use_boxcox))

    # train
    start = time.time()
    ets_train_h1 = apply_parallel_ets(
        ets_train_data_h1.groupby('drug_id'), ets_train_monthly,
        ets_params).reset_index(drop=True)
    end = time.time()
    logger.info('H1 ETS Train: Run time ' + str(round(end - start, 2)) + 'secs')
    # train error
    start = time.time()
    ets_train_error_h1 = ets_train_h1.groupby('drug_id').apply(
        train_error_ets_h1). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H1 ETS Error: Run time ' + str(round(end - start, 2)) + 'secs')
    # predict
    start = time.time()
    ets_predict_h1 = apply_parallel_ets(
        ets_train_data_h1.groupby('drug_id'), ets_predict_monthly,
        ets_train_h1).reset_index(drop=True)
    end = time.time()
    logger.info('H1 ETS Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    ''' # TODO - PROPHET TO BE INTG. LATER
    # FORECASTING MODULES: PROPHET

    prophet_train_data_h1 = drug_sales_monthly_bucket_h1.copy()
    prophet_train_data_h1 = prophet_train_data_h1[
        ['drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # model parameters
    horizon = 3 # future forecast
    # holts winter implementation
    n_changepoints_factor = 4
    changepoint_prior_scale = 0.2
    growth = 'linear'
    changepoint_range = 1
    interval_width = 0.68
    mcmc_samples = 0

    # train
    start = time.time()
    prophet_train_h1 = apply_parallel_prophet(
        prophet_train_data_h1.groupby('drug_id'), prophet_train_monthly,
        n_changepoints_factor, changepoint_prior_scale, growth,
        changepoint_range, interval_width, mcmc_samples, horizon, out_of_sample
    ).reset_index(drop=True)
    end = time.time()
    logger.info(
        'H1 Prophet Train: Run time ' + str(round(end-start, 2)) + 'secs')
    # train error
    start = time.time()
    prophet_train_error_h1 = prophet_train_h1.groupby('drug_id').\
        apply(train_error).reset_index(drop=True)
    end = time.time()
    logger.info(
        'H1 Prophet Error: Run time ' + str(round(end-start, 2)) + 'secs')
    # predict
    start = time.time()
    prophet_predict_h1 = apply_parallel_prophet(
        prophet_train_data_h1.groupby('drug_id'), prophet_predict_monthly,
        n_changepoints_factor, changepoint_prior_scale, growth,
        changepoint_range, interval_width, mcmc_samples, horizon, out_of_sample
    ).reset_index(drop=True)
    end = time.time()
    logger.info(
        'H1 Prophet Fcst: Run time ' + str(round(end-start, 2)) + 'secs')
    '''

    # FORECASTING MODULE - ENSEMBLE

    # identifying best model for each drug - using MA and ETS
    ensemble_error_h1 = ets_train_error_h1.merge(
        ma_train_error_h1, how='outer', on='drug_id', suffixes=('_ets', '_ma'))
    ensemble_error_h1['model'] = np.where(
        ensemble_error_h1['mape_ma'] < ensemble_error_h1['mape_ets'],
        'ma', 'ets')
    # choosing ma where SS days for ets is crossing 1 month
    ensemble_error_h1['ss_days_ets'] = 14.84 * ensemble_error_h1['std'] / \
                                       ensemble_error_h1['actual']
    ensemble_error_h1['model'] = np.where(ensemble_error_h1['ss_days_ets'] > 28,
                                          'ma', 'ets')
    ensemble_error_h1.loc[np.isnan(ensemble_error_h1['std']), 'model'] = 'ma'
    del ensemble_error_h1['actual']
    del ensemble_error_h1['std']
    del ensemble_error_h1['ss_days_ets']
    del ets_train_error_h1['actual']
    del ets_train_error_h1['std']
    ensemble_error_h1['mape'] = np.where(
        ensemble_error_h1['model'] == 'ma',
        ensemble_error_h1['mape_ma'], ensemble_error_h1['mape_ets'])
    ensemble_error_h1['mae'] = np.where(
        ensemble_error_h1['model'] == 'ma',
        ensemble_error_h1['mae_ma'], ensemble_error_h1['mae_ets'])

    # creating ensemble dataframe for best model - MA + ETS
    ma_drug_best_h1 = ensemble_error_h1.loc[
        ensemble_error_h1['model'] == 'ma', 'drug_id']
    ets_drug_best_h1 = ensemble_error_h1.loc[
        ensemble_error_h1['model'] == 'ets', 'drug_id']

    ma_train_best_h1 = ma_train_h1[
        ma_train_h1['drug_id'].isin(ma_drug_best_h1)]
    ma_predict_best_h1 = ma_predict_h1[
        ma_predict_h1['drug_id'].isin(ma_drug_best_h1)]
    ma_train_best_h1['model'] = 'ma'
    ma_predict_best_h1['model'] = 'ma'

    ets_train_best_h1 = ets_train_h1[
        ets_train_h1['drug_id'].isin(ets_drug_best_h1)]
    ets_predict_best_h1 = ets_predict_h1[
        ets_predict_h1['drug_id'].isin(ets_drug_best_h1)]
    ets_train_best_h1['model'] = 'ets'
    ets_predict_best_h1['model'] = 'ets'

    ensemble_train_h1 = pd.concat(
        [ma_train_best_h1, ets_train_best_h1], axis=0)
    ensemble_predict_h1 = pd.concat(
        [ma_predict_best_h1, ets_predict_best_h1], axis=0)

    ''' # TODO - PROPHET TO BE INTG. LATER
    # identifying best model for each drug - using MA, ETS and Prophet
    ensemble_error_h1 = ets_train_error_h1.merge(
        ma_train_error_h1, how='outer', on='drug_id',
        suffixes=('_ets', '_ma')).merge(
            prophet_train_error_h1, how='outer', on='drug_id',
              suffixes=('', '_prophet'))
    ensemble_error_h1.columns = [
        'drug_id', 'mae_ets', 'mape_ets', 'mae_ma', 'mape_ma',
        'mae_prophet', 'mape_prophet']
    ensemble_error_h1['model'] = np.select(
        [(ensemble_error_h1['mape_ma'] < ensemble_error_h1['mape_ets']) &
         (ensemble_error_h1['mape_ma'] < ensemble_error_h1['mape_prophet']),
         (ensemble_error_h1['mape_ets'] < ensemble_error_h1['mape_ma']) &
         (ensemble_error_h1['mape_ets'] < ensemble_error_h1['mape_prophet']),
         (ensemble_error_h1['mape_prophet'] < ensemble_error_h1['mape_ma']) &
         (ensemble_error_h1['mape_prophet'] < ensemble_error_h1['mape_ets'])],
        ['ma', 'ets', 'prophet'], default='ets')
    ensemble_error_h1['mape'] = np.select(
        [ensemble_error_h1['model'] == 'ma',
         ensemble_error_h1['model'] == 'ets',
         ensemble_error_h1['model'] == 'prophet'],
        [ensemble_error_h1['mape_ma'],
         ensemble_error_h1['mape_ets'],
        ensemble_error_h1['mape_prophet']],
        default=ensemble_error_h1['mape_ets'])
    ensemble_error_h1['mae'] = np.select(
        [ensemble_error_h1['model'] == 'ma',
         ensemble_error_h1['model'] == 'ets',
         ensemble_error_h1['model'] == 'prophet'],
        [ensemble_error_h1['mae_ma'],
         ensemble_error_h1['mae_ets'],
         ensemble_error_h1['mae_prophet']],
        default=ensemble_error_h1['mae_ets'])

    # creating ensemble dataframe for best model - MA + ETS + Prophet
    ma_drug_best_h1 = ensemble_error_h1.loc[
        ensemble_error_h1['model'] == 'ma', 'drug_id']
    ets_drug_best_h1 = ensemble_error_h1.loc[
        ensemble_error_h1['model'] == 'ets', 'drug_id']
    prophet_drug_best_h1 = ensemble_error_h1.loc[
        ensemble_error_h1['model'] == 'prophet', 'drug_id']

    ma_train_best_h1 = ma_train[
        ma_train_h1['drug_id'].isin(ma_drug_best_h1)]
    ma_predict_best_h1 = ma_predict[
        ma_predict['drug_id'].isin(ma_drug_best_h1)]
    ma_train_best_h1['model'] = 'ma'
    ma_predict_best_h1['model'] = 'ma'

    ets_train_best_h1 = ets_train_h1[
        ets_train_h1['drug_id'].isin(ets_drug_best_h1)]
    ets_predict_best_h1 = ets_predict_h1[
        ets_predict_h1['drug_id'].isin(ets_drug_best_h1)]
    ets_train_best_h1['model'] = 'ets'
    ets_predict_best_h1['model'] = 'ets'

    prophet_train_best_h1 = prophet_train_h1[
        prophet_train_h1['drug_id'].isin(prophet_drug_best_h1)]
    prophet_predict_best_h1 = prophet_predict_h1[
        prophet_predict_h1['drug_id'].isin(prophet_drug_best_h1)]
    prophet_train_best_h1['model'] = 'prophet'
    prophet_predict_best_h1['model'] = 'prophet'

    ensemble_train_h1 = pd.concat(
        [ma_train_best_h1, ets_train_best_h1, prophet_train_best_h1], axis=0)
    ensemble_predict_h1 = pd.concat(
        [ma_predict_best_h1, ets_predict_best_h1, prophet_predict_best_h1],
        axis=0)
    '''

    # H1 BUCKET AGGREGATING
    ma_train_h1['model'] = 'ma'
    ma_train_h1['history_bucket'] = 'H1'
    ets_train_h1['model'] = 'ets'
    ets_train_h1['history_bucket'] = 'H1'

    ma_train_error_h1['model'] = 'ma'
    ma_train_error_h1['history_bucket'] = 'H1'
    ets_train_error_h1['model'] = 'ets'
    ets_train_error_h1['history_bucket'] = 'H1'

    ma_predict_h1['model'] = 'ma'
    ma_predict_h1['history_bucket'] = 'H1'
    ets_predict_h1['model'] = 'ets'
    ets_predict_h1['history_bucket'] = 'H1'

    train_h1 = pd.concat([ma_train_h1, ets_train_h1], axis=0)
    train_error_h1 = pd.concat([ma_train_error_h1, ets_train_error_h1], axis=0)
    predict_h1 = pd.concat([ma_predict_h1, ets_predict_h1], axis=0)

    train_h1['forecast_type'] = 'train'
    train_h1['final_fcst'] = 'N'
    train_error_h1['forecast_type'] = 'train'
    train_error_h1['final_fcst'] = 'N'
    predict_h1['forecast_type'] = 'forecast'
    predict_h1['final_fcst'] = 'N'

    ensemble_train_h1['forecast_type'] = 'train'
    ensemble_train_h1['final_fcst'] = 'Y'
    ensemble_train_h1['history_bucket'] = 'H1'
    ensemble_error_h1['forecast_type'] = 'train'
    ensemble_error_h1['final_fcst'] = 'Y'
    ensemble_error_h1['history_bucket'] = 'H1'
    ensemble_predict_h1['forecast_type'] = 'forecast'
    ensemble_predict_h1['final_fcst'] = 'Y'
    ensemble_predict_h1['history_bucket'] = 'H1'

    ''' H2/H2- bucket - Train and Forecast'''
    logger.info(
        'Drugs for training' +
        str(drug_sales_monthly_bucket_h2.drug_id.nunique()))

    # FORECASTING MODULES: MOVING AVERAGES K=3

    ma_train_data_h2 = drug_sales_monthly_bucket_h2.copy()
    ma_train_data_h2 = ma_train_data_h2[
        ['drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # model parameters
    horizon = 3  # future forecast

    # train
    start = time.time()
    ma_train_h2 = ma_train_data_h2.groupby('drug_id').apply(ma_train_monthly). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H2 MA Train: Run time ' + str(round(end - start, 2)) + 'secs')
    # train error
    start = time.time()
    ma_train_error_h2 = ma_train_h2.groupby('drug_id').apply(train_error). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H2 MA Error: Run time ' + str(round(end - start, 2)) + 'secs')
    # predict
    start = time.time()
    ma_predict_h2 = ma_train_data_h2.groupby('drug_id'). \
        apply(ma_predict_monthly).reset_index(drop=True)
    end = time.time()
    logger.info('H2 MA Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    # FORECASTING MODULES: SIMPLE EXPONENTIAL SMOOTHING
    ses_train_data_h2 = drug_sales_monthly_bucket_h2.copy()
    ses_train_data_h2 = ses_train_data_h2[
        ['drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # variables
    horizon = 3  # future forecast
    out_of_sample = 3  # out of sample forecast
    # ses implementation
    trend = [None]
    seasonal = [None]
    damped = [False]
    seasonal_periods = [12]
    use_boxcox = [False]
    ses_params = list(
        product(trend, seasonal, damped, seasonal_periods, use_boxcox))

    # train
    start = time.time()
    ses_train_h2 = apply_parallel_ets(
        ses_train_data_h2.groupby('drug_id'), ets_train_monthly, ses_params
    ).reset_index(drop=True)
    end = time.time()
    logger.info('H2 ETS Train: Run time ' + str(round(end - start, 2)) + 'secs')
    # train error
    start = time.time()
    ses_train_error_h2 = ses_train_h2.groupby('drug_id').apply(train_error). \
        reset_index(drop=True)
    end = time.time()
    logger.info('H2 ETS Error: Run time ' + str(round(end - start, 2)) + 'secs')
    # predict
    start = time.time()
    ses_predict_h2 = apply_parallel_ets(
        ses_train_data_h2.groupby('drug_id'), ets_predict_monthly,
        ses_train_h2).reset_index(drop=True)
    end = time.time()
    logger.info('H2 ETS Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    # FORECASTING MODULE - ENSEMBLE

    # identifying best model for each drug - using MA and SES
    ensemble_error_h2 = ses_train_error_h2.merge(
        ma_train_error_h2, how='outer', on='drug_id', suffixes=('_ses', '_ma'))
    ensemble_error_h2['model'] = np.where(
        ensemble_error_h2['mape_ma'] < ensemble_error_h2['mape_ses'],
        'ma', 'ses')
    ensemble_error_h2['mape'] = np.where(
        ensemble_error_h2['model'] == 'ma',
        ensemble_error_h2['mape_ma'], ensemble_error_h2['mape_ses'])
    ensemble_error_h2['mae'] = np.where(
        ensemble_error_h2['model'] == 'ma',
        ensemble_error_h2['mae_ma'], ensemble_error_h2['mae_ses'])

    # creating ensemble dataframe for best_h2 model - MA + ses
    ma_drug_best_h2 = ensemble_error_h2.loc[
        ensemble_error_h2['model'] == 'ma', 'drug_id']
    ses_drug_best_h2 = ensemble_error_h2.loc[
        ensemble_error_h2['model'] == 'ses', 'drug_id']

    ma_train_best_h2 = ma_train_h2[
        ma_train_h2['drug_id'].isin(ma_drug_best_h2)]
    ma_predict_best_h2 = ma_predict_h2[
        ma_predict_h2['drug_id'].isin(ma_drug_best_h2)]
    ma_train_best_h2['model'] = 'ma'
    ma_predict_best_h2['model'] = 'ma'

    ses_train_best_h2 = ses_train_h2[
        ses_train_h2['drug_id'].isin(ses_drug_best_h2)]
    ses_predict_best_h2 = ses_predict_h2[
        ses_predict_h2['drug_id'].isin(ses_drug_best_h2)]
    ses_train_best_h2['model'] = 'ses'
    ses_predict_best_h2['model'] = 'ses'

    ensemble_train_h2 = pd.concat(
        [ma_train_best_h2, ses_train_best_h2], axis=0)

    # getting best model for H2- bucket
    ensemble_model_agg = ensemble_error_h2.groupby('model')['drug_id']. \
        count().reset_index()
    ensemble_model_best_h2 = ensemble_model_agg.loc[
        ensemble_model_agg['drug_id'] == ensemble_model_agg['drug_id'].max(),
        'model'].values[0]
    logger.info('Best model for H2 forecast' + ensemble_model_best_h2)

    # H2 minus bucket predic based on the best_h2 model overall
    train_data_h2minus = drug_sales_monthly_bucket_h2minus.copy()
    start = time.time()
    if ensemble_model_best_h2 == 'ses':
        start = time.time()
        train_data_h2minus['hyper_params'] = str(ses_params[0])
        predict_h2minus = apply_parallel_ets(
            train_data_h2minus.groupby('drug_id'), ets_predict_monthly,
            train_data_h2minus). \
            reset_index(drop=True)

    if ensemble_model_best_h2 == 'ma':
        start = time.time()
        predict_h2minus = train_data_h2minus.groupby('drug_id'). \
            apply(ma_predict_monthly).reset_index(drop=True)

    predict_h2minus['model'] = ensemble_model_best_h2
    end = time.time()
    logger.info(
        'H2 Minus Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    ensemble_predict_h2 = pd.concat(
        [ma_predict_best_h2, ses_predict_best_h2, predict_h2minus], axis=0)

    # H2 BUCKET AGGREGATING
    ma_train_h2['model'] = 'ma'
    ma_train_h2['history_bucket'] = 'H2'
    ses_train_h2['model'] = 'ses'
    ses_train_h2['history_bucket'] = 'H2'

    ma_train_error_h2['model'] = 'ma'
    ma_train_error_h2['history_bucket'] = 'H2'
    ses_train_error_h2['model'] = 'ses'
    ses_train_error_h2['history_bucket'] = 'H2'

    ma_predict_h2['model'] = 'ma'
    ma_predict_h2['history_bucket'] = 'H2'
    ses_predict_h2['model'] = 'ses'
    ses_predict_h2['history_bucket'] = 'H2'

    train_h2 = pd.concat([ma_train_h2, ses_train_h2], axis=0)
    train_error_h2 = pd.concat([ma_train_error_h2, ses_train_error_h2], axis=0)
    predict_h2 = pd.concat([ma_predict_h2, ses_predict_h2], axis=0)

    train_h2['forecast_type'] = 'train'
    train_h2['final_fcst'] = 'N'
    train_error_h2['forecast_type'] = 'train'
    train_error_h2['final_fcst'] = 'N'
    predict_h2['forecast_type'] = 'forecast'
    predict_h2['final_fcst'] = 'N'

    ensemble_train_h2['forecast_type'] = 'train'
    ensemble_train_h2['final_fcst'] = 'Y'
    ensemble_train_h2['history_bucket'] = 'H2'
    ensemble_error_h2['forecast_type'] = 'train'
    ensemble_error_h2['final_fcst'] = 'Y'
    ensemble_error_h2['history_bucket'] = 'H2'
    ensemble_predict_h2['forecast_type'] = 'forecast'
    ensemble_predict_h2['final_fcst'] = 'Y'
    ensemble_predict_h2['history_bucket'] = 'H2'

    ''' H3- bucket - Train and Forecast'''
    logger.info(
        'Drugs for training' +
        str(drug_sales_monthly_bucket_h2.drug_id.nunique()))

    # FORECASTING MODULES: NAIVE

    naive_train_data_h3 = drug_sales_monthly_bucket_h3.copy()
    naive_train_data_h3 = naive_train_data_h3[[
        'drug_id', 'month_begin_dt', 'year', 'month', 'net_sales_quantity']]

    # predict
    start = time.time()
    naive_predict_h3 = naive_train_data_h3.groupby('drug_id'). \
        apply(naive_predict_monthly, horizon).reset_index(drop=True)
    end = time.time()
    logger.info(
        'H3 Naive Fcst: Run time ' + str(round(end - start, 2)) + 'secs')

    # H3 BUCKET AGGREGATING
    naive_predict_h3['model'] = 'naive'
    naive_predict_h3['history_bucket'] = 'H3'

    predict_h3 = naive_predict_h3.copy()
    predict_h3['forecast_type'] = 'forecast'
    predict_h3['final_fcst'] = 'N'

    ensemble_predict_h3 = naive_predict_h3.copy()
    ensemble_predict_h3['forecast_type'] = 'forecast'
    ensemble_predict_h3['final_fcst'] = 'Y'

    ''' AGG. TRAIN/ERROR/FORECAST TABLES '''
    train = pd.concat([train_h1, train_h2], axis=0)
    error = pd.concat([train_error_h1, train_error_h2], axis=0)
    predict = pd.concat([predict_h1, predict_h2, predict_h3], axis=0)

    ensemble_train = pd.concat([ensemble_train_h1, ensemble_train_h2], axis=0)
    ensemble_error = pd.concat([ensemble_error_h1, ensemble_error_h2], axis=0)
    ensemble_predict = pd.concat(
        [ensemble_predict_h1, ensemble_predict_h2, ensemble_predict_h3],
        axis=0)

    # Letting code to not fail when h3 bucket is empty
    if 'net_sales_quantity' in predict.columns:
        del predict['net_sales_quantity']
    if 'net_sales_quantity' in ensemble_predict.columns:
        del ensemble_predict['net_sales_quantity']

    # converting data to str objection
    train['month_begin_dt'] = train['month_begin_dt']. \
        dt.date.astype(str)
    predict['month_begin_dt'] = predict['month_begin_dt']. \
        dt.date.astype(str)
    ensemble_train['month_begin_dt'] = ensemble_train['month_begin_dt']. \
        dt.date.astype(str)
    ensemble_predict['month_begin_dt'] = ensemble_predict['month_begin_dt']. \
        dt.date.astype(str)

    return train, error, predict, ensemble_train, ensemble_error, \
           ensemble_predict
