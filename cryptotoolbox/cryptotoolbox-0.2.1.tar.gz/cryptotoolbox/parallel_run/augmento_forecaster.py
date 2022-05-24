#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

from cryptotoolbox.file_saver import dropbox_file_saver

from cryptotoolbox.forecasting import forecasting_utility
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from cryptotoolbox.signal import signal_utility
from cryptotoolbox.rebalancing import time_series
from cryptotoolbox.utility import metrics
import datetime
from cryptotoolbox.utility import date_utility
from cryptotoolbox.statistics import tester
import json

import pandas as pd
import numpy as np

from dateutil import parser
from cryptotoolbox.features import easy_feature


def rescalize(y, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (y - range1[0]) / delta1) + range2[0]

class AbstractRunner(ABC):
    def __init__(self, starting_date = None, running_date = None, drop_token=None, dropbox_backup = True, underlying=None, frequence = None, target='target', local_root_directory='../data/', user = 'napoleon', number_per_year=252, augmento_suffix = '_augmento.pkl'):
        super().__init__()
        self.starting_date = starting_date
        self.running_date = running_date
        self.underlying = underlying
        self.frequence=frequence
        self.target=target
        self.local_root_directory=local_root_directory
        self.user=user
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.running_date = running_date
        self.starting_date = starting_date
        self.number_per_year = number_per_year

        self.augmento_suffix = augmento_suffix
        self.dates_stub = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y')


        self.predictors_output_file_name = f'{self.underlying}_{self.frequence}_{self.dates_stub}{self.augmento_suffix}'

        @abstractmethod
        def runTrial(self, saver, seed, n, s, s_eval, calibration_step, signal_type, idios_string):
            pass

class  Augmento_ForecasterRunner(AbstractRunner):

    processed_advanced_features_df = None

    def runTrial(self, saver, seed, adv_feat, n, s, s_eval, calibration_step, signal_type, idios_string):
        continuous_saving_key, continuous_saving_key_scale_one, continuous_saving_key_scale_two, two_states_saving_key, two_states_saving_key_lo, three_states_saving_key, three_states_saving_key_lo, idios = saver.create_saving_key(
            seed, adv_feat, n, s, s_eval, calibration_step, signal_type, idios_string)

        check_run_existence, table_number = saver.checkRunExistence(continuous_saving_key)
        exhaustive_check_run_existence, exhaustive_table_number = saver.exhaustiveCheckRunExistence(continuous_saving_key)
        assert check_run_existence == exhaustive_check_run_existence
        if check_run_existence:
            assert table_number == exhaustive_table_number
        if check_run_existence:
            return
        if n == 0:
            n = None
        if s_eval == 0:
            s_eval = None

        idios.update({'number_per_year' : self.number_per_year})

        if adv_feat:
            if Augmento_ForecasterRunner.processed_advanced_features_df is None:
                if self.dropbox_backup:
                    print(f'downoading from dropbox {self.predictors_output_file_name}')
                    timeseries_df = self.dbx.download_pkl(self.predictors_output_file_name)
                else:
                    full_path = self.local_root_directory + self.predictors_output_file_name
                    print(f'reading file from local disk {full_path}')
                    timeseries_df = pd.read_pickle(full_path)
                    print('size before filtering')
                    print(timeseries_df.shape)
                features_names = [col for col in timeseries_df.columns if
                                  col not in ['close', 'high', 'low', 'open', 'volume']]
                for me_feature in features_names:
                    print(f'processing {me_feature}')
                    timeseries_df = easy_feature.easyFeature(features=timeseries_df, feature_name=me_feature)
                Augmento_ForecasterRunner.processed_advanced_features_df=timeseries_df
            else:
                timeseries_df = Augmento_ForecasterRunner.processed_advanced_features_df.copy()
        else:
            if self.dropbox_backup:
                print(f'downoading from dropbox {self.predictors_output_file_name}')
                timeseries_df = self.dbx.download_pkl(self.predictors_output_file_name)
            else:
                full_path = self.local_root_directory + self.predictors_output_file_name
                print(f'reading file from local disk {full_path}')
                timeseries_df = pd.read_pickle(full_path)
                print('size before filtering')
                print(timeseries_df.shape)

        if 'Date' in timeseries_df.columns:
            print('dropping the date column')
            timeseries_df=timeseries_df.drop(columns=['Date'])

        timeseries_df=timeseries_df[timeseries_df.index >= self.starting_date]
        timeseries_df=timeseries_df[timeseries_df.index <= self.running_date]
        print('size after filtering')
        print(timeseries_df.shape)
        # date_utility.add_datepart(timeseries_df, 'date', False)
        # timeseries_df = timeseries_df.fillna(0)
        generic_columns = ['open', 'high', 'low', 'close', 'volume']
        features_colmuns = [col for col in timeseries_df.columns if col not in generic_columns]

        timeseries_df['close_return']= timeseries_df['close'].pct_change()


        timeseries_df['shifted_close_return']= timeseries_df['close'].pct_change().shift(-1)
        timeseries_df=timeseries_df.iloc[:-1]
        y_true = timeseries_df['close_return']
        X, y = timeseries_df.loc[:, features_colmuns], timeseries_df[self.target]
        print('predictors shape')
        print(X.shape)
        print('output shape')
        print(y.shape)


        chosen_method = signal_type
        model = forecasting_utility.instantiate_model(method=chosen_method, idios = idios)

        # Compute rolling weights
        forecasted_series, features_importances, discrete_two_states_forecasting_series, discrete_two_states_forecasting_series_lo, discrete_three_states_forecasting_series, discrete_three_states_forecasting_series_lo = time_series.rolling_forecasting(
            model,
            X,
            y,
            n=n,
            s=s,
            s_eval = s_eval,
            calibration_step = calibration_step,
            method = chosen_method,
            display = True)

        forecasted_series = forecasted_series.shift(1)
        discrete_two_states_forecasting_series = discrete_two_states_forecasting_series.shift(1)
        discrete_two_states_forecasting_series_lo = discrete_two_states_forecasting_series_lo.shift(1)
        discrete_three_states_forecasting_series = discrete_three_states_forecasting_series.shift(1)
        discrete_three_states_forecasting_series_lo = discrete_three_states_forecasting_series_lo.shift(1)

        print('mixing backtest done')
        features_importances = features_importances.sum(axis = 0)
        print('features importance')
        print(features_importances.sum())

        forecasted_series[np.isnan(forecasted_series)] = 0
        forecasted_series[np.isinf(forecasted_series)] = 0
        discrete_two_states_forecasting_series[np.isnan(discrete_two_states_forecasting_series)] = 0
        discrete_two_states_forecasting_series[np.isinf(discrete_two_states_forecasting_series)] = 0
        discrete_two_states_forecasting_series_lo[np.isnan(discrete_two_states_forecasting_series_lo)] = 0
        discrete_two_states_forecasting_series_lo[np.isinf(discrete_two_states_forecasting_series_lo)] = 0
        discrete_three_states_forecasting_series[np.isnan(discrete_three_states_forecasting_series)] = 0
        discrete_three_states_forecasting_series[np.isinf(discrete_three_states_forecasting_series)] = 0
        discrete_three_states_forecasting_series_lo[np.isnan(discrete_three_states_forecasting_series_lo)] = 0
        discrete_three_states_forecasting_series_lo[np.isinf(discrete_three_states_forecasting_series_lo)] = 0
        y[np.isnan(y)] = 0
        y[np.isinf(y)] = 0
        matrix = confusion_matrix(y > 0, discrete_two_states_forecasting_series)
        rmse = mean_squared_error(y, forecasted_series)
        accuracy = accuracy_score(y > 0, discrete_two_states_forecasting_series)


        print('rmse '  + str(rmse))
        print('accuracy')
        print(accuracy)
        print('confusion matrix')
        print(matrix)

        transaction_cost = True
        if self.frequence=='minutely':
            transaction_cost = False
            # saving the continuous signal
        print('max prediction signal')
        print(max(forecasted_series))
        print('min prediction signal')
        print(min(forecasted_series))
        scale_one = 2.
        forecasted_series_scale_one = rescalize(forecasted_series, [min(forecasted_series), max(forecasted_series)],
                                                [-scale_one, scale_one])
        scale_two = 1.
        forecasted_series_scale_two = rescalize(forecasted_series, [min(forecasted_series), max(forecasted_series)],
                                                [-scale_two, scale_two])
        scale_three = 0.5
        forecasted_series_scale_three = rescalize(forecasted_series, [min(forecasted_series), max(forecasted_series)],
                                                  [-scale_three, scale_three])

        forecasted_series_scale_one = np.clip(forecasted_series_scale_one, a_min=-1., a_max=1.)
        forecasted_series_scale_two = np.clip(forecasted_series_scale_two, a_min=-1., a_max=1.)
        forecasted_series_scale_three = np.clip(forecasted_series_scale_three, a_min=-1., a_max=1.)

        print('scale one max prediction signal')
        print(max(forecasted_series_scale_one))
        print('scale one min prediction signal')
        print(min(forecasted_series_scale_one))

        print('scale two max prediction signal')
        print(max(forecasted_series_scale_two))
        print('scale two min prediction signal')
        print(min(forecasted_series_scale_two))

        print('scale three max prediction signal')
        print(max(forecasted_series_scale_three))
        print('scale three min prediction signal')
        print(min(forecasted_series_scale_three))

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_one, y_true=y_true,
                                                              transaction_cost=transaction_cost, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key, perf_df)

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_two, y_true=y_true,
                                                              transaction_cost=transaction_cost, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key_scale_one, perf_df)

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_three, y_true=y_true,
                                                              transaction_cost=transaction_cost, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key_scale_two, perf_df)

        # saving the 2 states signal
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_two_states_forecasting_series,
                                                              y_true=y_true, transaction_cost=transaction_cost,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(two_states_saving_key, perf_df)

        # saving the 2 states signal long only
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_two_states_forecasting_series_lo,
                                                              y_true=y_true,
                                                              transaction_cost=transaction_cost, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(two_states_saving_key_lo, perf_df)

        # saving the 3 states signal
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_three_states_forecasting_series,
                                                              y_true=y_true, transaction_cost=transaction_cost,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(three_states_saving_key, perf_df)

        # saving the 3 states signal long only
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_three_states_forecasting_series_lo,
                                                              y_true=y_true,
                                                              transaction_cost=transaction_cost, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(three_states_saving_key_lo, perf_df)