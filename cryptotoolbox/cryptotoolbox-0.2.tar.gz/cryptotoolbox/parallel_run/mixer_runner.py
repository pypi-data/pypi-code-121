#!/usr/bin/env python
# coding: utf-8

from __future__ import division

from abc import ABC, abstractmethod

from cryptotoolbox.file_saver import dropbox_file_saver

from cryptotoolbox.mixing import mixing_utility
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from cryptotoolbox.signal import signal_utility
from cryptotoolbox.rebalancing import time_series
from cryptotoolbox.utility import metrics
import datetime

import json

import pandas as pd
import numpy as np


def rescalize(y, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (y - range1[0]) / delta1) + range2[0]


class AbstractRunner(ABC):
    def __init__(self, filtering_date = None, starting_date = None, running_date = None, calibration_starting_date = None,  calibration_running_date = None, drop_token=None, dropbox_backup = True, underlying=None, frequence = None, selected_algo=None, aggregated_pkl_file_suffix='freqly_to_mix.pkl', aggregated_pkl_mapping_file_suffix = 'freqly_to_mix_mapping.pkl', list_pkl_file_suffix = 'my_list.pkl', local_root_directory='../data/', user = 'napoleon',number_per_year=252, delay = 0):
        super().__init__()
        if filtering_date is None :
            filtering_date = starting_date

        self.filtering_date = filtering_date

        self.starting_date = starting_date
        self.running_date = running_date

        self.calibration_starting_date = calibration_starting_date
        self.calibration_running_date = calibration_running_date

        self.aggregated_pkl_file_suffix=aggregated_pkl_file_suffix
        self.aggregated_pkl_mapping_file_suffix=aggregated_pkl_mapping_file_suffix
        self.underlying = underlying
        self.list_pkl_file_suffix = list_pkl_file_suffix
        self.frequence=frequence
        self.selected_algo=selected_algo
        self.delay = delay

        self.calibrating_dates_stub = self.calibration_starting_date.strftime('%d_%b_%Y') + '_' + self.calibration_running_date.strftime('%d_%b_%Y')
        self.dates_stub = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y')

        if self.frequence == 'daily':
            self.list_pkl_file_name = self.calibrating_dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.list_pkl_file_suffix
            self.aggregated_pkl_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + '_' + str(
                self.delay) + self.aggregated_pkl_file_suffix
            self.aggregated_pkl_mapping_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + '_' + str(
                self.delay) + self.aggregated_pkl_mapping_file_suffix
        else:
            self.list_pkl_file_name = self.calibrating_dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.list_pkl_file_suffix
            self.aggregated_pkl_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.aggregated_pkl_file_suffix
            self.aggregated_pkl_mapping_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.aggregated_pkl_mapping_file_suffix

        self.local_root_directory=local_root_directory
        self.user=user
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.running_date = running_date
        self.starting_date = starting_date
        self.starting_iterations_to_pass = 20
        self.number_per_year = number_per_year



    @abstractmethod
    def runTrial(self,saver,  seed,  n, s, s_eval, calibration_step, transaction_costs, signal_type, idios_string):
        pass

class  MixerRunner(AbstractRunner):
    def runTrial(self, saver, seed, n, s, s_eval, calibration_step, transaction_costs, signal_type, idios_string):
        continuous_saving_key, continuous_saving_key_scale_one, continuous_saving_key_scale_two, two_states_saving_key, two_states_saving_key_lo, three_states_saving_key, three_states_saving_key_lo, idios = saver.create_saving_key(seed, n, s, s_eval, calibration_step, transaction_costs, signal_type, idios_string)

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

        if self.dropbox_backup:
            print(self.list_pkl_file_name)
            aggregated_csv_file_name = self.aggregated_pkl_file_name.replace('pkl', 'csv')
            aggregated_csv_mapping_file_name = self.aggregated_pkl_mapping_file_name.replace('pkl', 'csv')
            raw_data = self.dbx.download_csv(csv_file_name=aggregated_csv_file_name, index_date=True)
            mapping_data = self.dbx.download_csv(csv_file_name=aggregated_csv_mapping_file_name, index_date=True)
        else:
            print(f'reading {self.local_root_directory + self.aggregated_pkl_file_name}')
            raw_data = pd.read_pickle(self.local_root_directory + self.aggregated_pkl_file_name)
            print(f'reading mapping {self.local_root_directory + self.aggregated_pkl_mapping_file_name}')
            mapping_data = pd.read_pickle(self.local_root_directory + self.aggregated_pkl_mapping_file_name)

        print('size before filtering')
        print(raw_data.shape)

        raw_data=raw_data[raw_data.index >= max((self.starting_date+datetime.timedelta(days=self.starting_iterations_to_pass)), self.filtering_date)]
        raw_data=raw_data[raw_data.index <= self.running_date]

        print('size after filtering')
        print(raw_data.shape)
        raw_data['close_return'] = raw_data['close'].pct_change()
        raw_data['shifted_close_return'] = raw_data['close_return'].shift(-1)
        raw_data = raw_data.iloc[:-1]
        y_true = raw_data['close_return']


        y = raw_data['shifted_close_return']
        X = raw_data[[col for col in raw_data.columns if 'signal' in col]]

        print('predictors shape')
        print(X.shape)
        print('output shape')
        print(y.shape)
        chosen_method = signal_type
        model = mixing_utility.instantiate_model(method=chosen_method)

        # Compute rolling weights
        forecasted_series, features_importances, discrete_two_states_forecasting_series, discrete_two_states_forecasting_series_lo, discrete_three_states_forecasting_series, discrete_three_states_forecasting_series_lo = time_series.rolling_mixing(
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

        # transaction_cost = self.apply_transaction_cost
        # if self.frequence=='minutely':
        #     transaction_cost = False

        #saving the continuous signal
        print('max prediction signal')
        print(max(forecasted_series))
        print('min prediction signal')
        print(min(forecasted_series))
        scale_one = 2.
        forecasted_series_scale_one = rescalize(forecasted_series, [min(forecasted_series),max(forecasted_series)],[-scale_one,scale_one])
        scale_two = 1.
        forecasted_series_scale_two = rescalize(forecasted_series, [min(forecasted_series),max(forecasted_series)],[-scale_two,scale_two])
        scale_three = 0.5
        forecasted_series_scale_three = rescalize(forecasted_series, [min(forecasted_series),max(forecasted_series)],[-scale_three,scale_three])

        forecasted_series_scale_one=np.clip(forecasted_series_scale_one,a_min=-1.,a_max=1.)
        forecasted_series_scale_two=np.clip(forecasted_series_scale_two,a_min=-1.,a_max=1.)
        forecasted_series_scale_three=np.clip(forecasted_series_scale_three,a_min=-1.,a_max=1.)

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

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_one, y_true = y_true, transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period= self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period= self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key, perf_df)

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_two, y_true = y_true, transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period= self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period= self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key_scale_one, perf_df)

        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=forecasted_series_scale_three, y_true = y_true, transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period= self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period= self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(continuous_saving_key_scale_two, perf_df)


        #saving the 2 states signal
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred= discrete_two_states_forecasting_series , y_true = y_true, transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period= self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period= self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(two_states_saving_key, perf_df)

        # saving the 2 states signal long only
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_two_states_forecasting_series_lo, y_true=y_true,
                                                              transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(two_states_saving_key_lo, perf_df)


        #saving the 3 states signal
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_three_states_forecasting_series, y_true = y_true, transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period= self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period= self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(three_states_saving_key, perf_df)

        # saving the 3 states signal long only
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=discrete_three_states_forecasting_series_lo, y_true=y_true,
                                                              transaction_cost=transaction_costs, print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=self.number_per_year, from_ret=True)
        sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=self.number_per_year, from_ret=True)
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        saver.saveAll(three_states_saving_key_lo, perf_df)