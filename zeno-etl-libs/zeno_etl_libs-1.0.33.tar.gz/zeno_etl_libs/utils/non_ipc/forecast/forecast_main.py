'''
Author - vishal.gupta@generico.in
Objective - non ipc forecast reset main script
'''

import time
import pandas as pd

from itertools import product
from zeno_etl_libs.utils.warehouse.forecast.moving_average import ma_train_monthly,\
    ma_predict_monthly
from zeno_etl_libs.utils.warehouse.forecast.ets import ets_train_monthly,\
    ets_predict_monthly
from zeno_etl_libs.utils.warehouse.forecast.errors import train_error
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import apply_parallel_ets
from zeno_etl_libs.utils.non_ipc.forecast.\
    helper_functions import non_ipc_error_report, apply_parallel_croston
from zeno_etl_libs.utils.non_ipc.forecast.croston import croston_train_weekly,\
    croston_predict_weekly
from zeno_etl_libs.utils.non_ipc.forecast.\
    ensemble_champion import ensemble_champion
from zeno_etl_libs.utils.non_ipc.forecast.\
    ensemble_minimisation import ensemble_minimisation


def non_ipc_forecast(
        drug_sales_monthly, drug_data_weekly, drug_class, out_of_sample,
        horizon, train_flag, logger=None, kind='mae'):

    if train_flag:

        '''BASE FORECASTING - NAIVE'''
        logger.info('STARTING NAIVE TRAINING AND FORECAST')

        # making copy for data
        naive_train_data = drug_sales_monthly.copy()
        naive_train_data.rename(columns={'date': 'month_begin_dt'}, inplace=True)

        k = 1  # for naive using the ma train function
        # train
        start = time.time()
        naive_train = naive_train_data.groupby('drug_id').apply(
            ma_train_monthly, k, out_of_sample).\
            reset_index(drop=True)
        end = time.time()
        logger.info('Naive Train: Run time ' + str(round(end-start, 2)) + 'secs')

        # train error
        start = time.time()
        naive_train_error = naive_train.groupby('drug_id').apply(train_error).\
            reset_index(drop=True)
        end = time.time()
        logger.info('Naive Error: Run time ' + str(round(end-start, 2)) + 'secs')

        # predict
        start = time.time()
        naive_predict = naive_train_data.groupby('drug_id').\
            apply(ma_predict_monthly, k, out_of_sample).reset_index(drop=True)
        end = time.time()
        logger.info('Naive Fcst: Run time ' + str(round(end-start, 2)) + 'secs')

        # Naive error reports
        # _ = non_ipc_error_report(naive_train_error, naive_train, drug_class)

        # model informations
        naive_train['hyper_params'] = ''
        naive_train['model'] = 'naive'
        naive_train_error['model'] = 'naive'
        naive_predict['model'] = 'naive'

        '''BASE FORECASTING - MOVING AVERAGE'''
        logger.info('STARTING MOVING AVERAGE TRAINING AND FORECAST')

        ma_train_data = drug_sales_monthly.copy()
        ma_train_data.rename(columns={'date': 'month_begin_dt'}, inplace=True)

        k = 3  # for MA3
        # train
        start = time.time()
        ma_train = ma_train_data.groupby('drug_id').apply(
            ma_train_monthly, k, out_of_sample).\
            reset_index(drop=True)
        end = time.time()
        logger.info('MA Train: Run time ' + str(round(end-start, 2)) + 'secs')

        # train error
        start = time.time()
        ma_train_error = ma_train.groupby('drug_id').apply(train_error).\
            reset_index(drop=True)
        end = time.time()
        logger.info('MA Error: Run time ' + str(round(end-start, 2)) + 'secs')

        # predict
        start = time.time()
        ma_predict = ma_train_data.groupby('drug_id').\
            apply(ma_predict_monthly, k, out_of_sample).reset_index(drop=True)
        end = time.time()
        logger.info('MA Fcst: Run time ' + str(round(end-start, 2)) + 'secs')

        # Moving average error reports
        # _ = non_ipc_error_report(ma_train_error, ma_train, drug_class)

        # model informations
        ma_train['hyper_params'] = ''
        ma_train['model'] = 'ma'
        ma_train_error['model'] = 'ma'
        ma_predict['model'] = 'ma'

        '''BASE FORECASTING - EXPONENTIAL SMOOTHING'''
        logger.info('STARTING ESM TRAINING AND FORECAST')

        # model parameters
        # holts winter implementation - single, double and triple exponential
        trend = ['additive', None]
        seasonal = ['additive', None]
        damped = [True, False]
        seasonal_periods = [12]
        use_boxcox = [True, False]
        ets_params = list(
            product(trend, seasonal, damped, seasonal_periods, use_boxcox))

        ets_train_data = drug_sales_monthly.copy()
        ets_train_data.rename(columns={'date': 'month_begin_dt'}, inplace=True)

        # train
        start = time.time()
        ets_train = apply_parallel_ets(
            ets_train_data.groupby('drug_id'), ets_train_monthly,
            ets_params, horizon, out_of_sample).reset_index(drop=True)
        end = time.time()
        logger.info('ETS Train: Run time ' + str(round(end-start, 2)) + 'secs')

        # train error
        start = time.time()
        ets_train_error = ets_train.groupby('drug_id').apply(train_error).\
            reset_index(drop=True)
        end = time.time()
        logger.info('ETS Error: Run time ' + str(round(end-start, 2)) + 'secs')

        # predict
        start = time.time()
        ets_predict = apply_parallel_ets(
            ets_train_data.groupby('drug_id'), ets_predict_monthly,
            ets_train, horizon, out_of_sample).reset_index(drop=True)
        end = time.time()
        logger.info('ETS Fcst: Run time ' + str(round(end-start, 2)) + 'secs')

        # Exponential smoothing error reports
        # _ = non_ipc_error_report(ets_train_error, ets_train, drug_class)

        # model information
        ets_train['model'] = 'ets'
        ets_train_error['model'] = 'ets'
        ets_predict['model'] = 'ets'

        '''BASE FORECASTING - CROSTON FOR C BUCKET'''
        logger.info('STARTING CROSTON TRAINING AND FORECAST')

        # getting drug list for C bucket
        c_bucket_drug_list = list(
            drug_class[drug_class['bucket_abc'] == 'C']['drug_id'])
        logger.info('No of drugs in Bucket C for Croston' +
                    str(len(c_bucket_drug_list)))

        croston_train_data = drug_data_weekly.copy()
        croston_train_data = croston_train_data[
            croston_train_data['drug_id'].isin(c_bucket_drug_list)]
        croston_train_data.rename(columns={'date': 'month_begin_dt'}, inplace=True)

        # Runtime parameters
        croston_out_of_sample = 4
        croston_horizon = 4
        croston_params = (0.5, 0.5)

        # train
        start = time.time()
        croston_train = apply_parallel_croston(
            croston_train_data.groupby('drug_id'), croston_train_weekly,
            croston_horizon, croston_out_of_sample, croston_params).\
            reset_index(drop=True)
        end = time.time()
        logger.info('Croston Train: Run time ' + str(round(end-start, 2)) + 'secs')
        # train error
        start = time.time()
        croston_train_error = croston_train.groupby('drug_id').\
            apply(train_error).\
            reset_index(drop=True)
        end = time.time()
        logger.info('Croston Error: Run time ' + str(round(end-start, 2)) + 'secs')
        # predict
        start = time.time()
        croston_predict = apply_parallel_croston(
            croston_train_data.groupby('drug_id'), croston_predict_weekly,
            croston_horizon, croston_out_of_sample, croston_params).\
            reset_index(drop=True)
        end = time.time()
        logger.info('Croston Fcst: Run time ' + str(round(end-start, 2)) + 'secs')

        # Croston error reports
        # _ = non_ipc_error_report(croston_train_error, croston_train, drug_class)

        # model information
        croston_train['model'] = 'croston'
        croston_train_error['model'] = 'croston'
        croston_predict['model'] = 'croston'

        '''BASE MODELS: COMBINING'''
        train = [naive_train, ma_train, ets_train, croston_train]
        error = [
            naive_train_error, ma_train_error, ets_train_error,
            croston_train_error]
        predict = [naive_predict, ma_predict, ets_predict, croston_predict]

        base_train = pd.concat(train, axis=0)
        base_train['final_fcst'] = 'N'
        base_train_error = pd.concat(error, axis=0)
        base_train_error['final_fcst'] = 'N'
        base_predict = pd.concat(predict, axis=0)
        base_predict['final_fcst'] = 'N'

        '''ENSEMBLE FORECASTING - CHAMPION MODEL'''
        logger.info('STARTING ENSEMBLE CHAMPION MODEL SELECTION')

        champion_train, champion_train_error, champion_predict = ensemble_champion(
            train, error, predict, logger)
        champion_train['model'] = 'champion_' + champion_train['model']
        champion_train_error['model'] = 'champion_' + champion_train_error['model']
        champion_predict['model'] = 'champion_' + champion_predict['model']
        champion_train['final_fcst'] = 'Y'
        champion_train_error['final_fcst'] = 'Y'
        champion_predict['final_fcst'] = 'Y'

        # Champion model ensmeble training errors
        # _ = non_ipc_error_report(champion_train_error, champion_train, drug_class)

        '''ENSEMBLE FORECASTING - SSE MINIMISATION'''
        optimised_train, optimised_train_error,\
            optimised_predict = ensemble_minimisation(
                train, error, predict, kind, logger)
        optimised_train['final_fcst'] = 'N'
        optimised_train_error['final_fcst'] = 'N'
        optimised_predict['final_fcst'] = 'N'

        # Optimised errors model ensmeble training errors
        # _ = non_ipc_error_report(
        #     optimised_train_error, optimised_train, drug_class)

        '''BASE MODELS: COMBINING'''
        ensemble_train = [champion_train, optimised_train]
        ensemble_error = [champion_train_error, optimised_train_error]
        ensemble_predict = [champion_predict, optimised_predict]

        ensemble_train = pd.concat(ensemble_train, axis=0)
        ensemble_error = pd.concat(ensemble_error, axis=0)
        ensemble_predict = pd.concat(ensemble_predict, axis=0)

    else:
        '''BASE FORECASTING - SIMPLE EXPONENTIAL SMOOTHING'''
        logger.info('STARTING SES FORECAST')

        # model parameters
        # holts winter implementation - single exponential
        trend = [None]
        seasonal = [None]
        damped = [False]
        seasonal_periods = [12]
        use_boxcox = [False]
        ses_params = list(
            product(trend, seasonal, damped, seasonal_periods, use_boxcox))

        ses_train_data = drug_sales_monthly.copy()
        ses_train_data.rename(columns={'date': 'month_begin_dt'}, inplace=True)
        ses_train_data['hyper_params'] = str(ses_params[0])

        # predict
        start = time.time()
        ses_predict = apply_parallel_ets(
            ses_train_data.groupby('drug_id'), ets_predict_monthly,
            ses_train_data, horizon, out_of_sample).reset_index(drop=True)
        end = time.time()
        logger.info('ETS Fcst: Run time ' + str(round(end-start, 2)) + 'secs')

        # model information
        ses_predict['model'] = 'ses'

        # creating final return df
        base_train = pd.DataFrame()
        base_train_error = pd.DataFrame()
        base_predict = pd.DataFrame()

        ensemble_train = pd.DataFrame()
        ensemble_error = pd.DataFrame()
        ensemble_predict = ses_predict
        ensemble_predict['final_fcst'] = 'Y'


    return base_train, base_train_error,\
        base_predict, ensemble_train, ensemble_error, ensemble_predict
