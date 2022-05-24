#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.signal import signal_generator
from cryptotoolbox.connector import napoleon_connector
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.parallel_run import signal_result_analyzer
from cryptotoolbox.parallel_run import launcher_utility
import json

from pathlib import Path

def daily_bc_apply_standard_mean_discretization(signals_df=None, s=21, method ='find_best_three_states_discretization_lo'):
    day_signal_columns = [me_sig for me_sig in signals_df.columns if 'signal' in me_sig ]
    signals_np = signals_df[day_signal_columns].values  # [:, len(self.generic_columns):]
    full_y_true = signals_df['close'].pct_change().fillna(0.)
    y_pred_discretized = np.zeros(full_y_true.shape)
    for row_index in range(s, signals_np.shape[0]):
        starting_train = row_index - s
        stopping_train = row_index
        prediction = row_index
        rolling_np = signals_np[starting_train:stopping_train, :]
        y_train_true = full_y_true[starting_train:stopping_train]
        y_train_pred = np.mean(rolling_np, axis=1)

        if method == 'find_best_three_states_discretization':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(signals_np[row_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states(y_next_pred, upper_threshold,
                                                                                    lower_threshold)
        elif method == 'find_best_three_states_discretization_lo':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(signals_np[row_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states_lo(y_next_pred, upper_threshold,
                                                                                       lower_threshold)
        elif method == 'find_best_two_states_discretization':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(
                y_train_pred, y_train_true)

            y_next_pred = np.nanmean(signals_np[row_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states(y_next_pred, splitting_threshold)
        elif method == 'find_best_two_states_discretization_lo':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(signals_np[row_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states_lo(y_next_pred, splitting_threshold)

        y_pred_discretized[prediction] = y_next_pred_discrete
    return y_pred_discretized

class AbstractRunner(ABC):
    def __init__(self, calibration_starting_date = None,  calibration_running_date = None, starting_date = None,  running_date = None,  drop_token=None, dropbox_backup = True, underlying = None, frequence='daily', selected_algo='',algo='' ,freqly_return_pkl_filename_suffix='freqly_candels.pkl',aggregated_pkl_file_suffix='freqly_to_mix.pkl', aggregated_pkl_mapping_file_suffix = 'freqly_to_mix_mapping.pkl', list_pkl_file_suffix = 'my_list.pkl', local_root_directory='../data/', user = 'napoleon', add_turn_over = False, skipping_size=200, recompute_all = True, db_path_suffix=None, daily_ia_lookback_window=21, delay = 0):
        super().__init__()
        self.starting_date = starting_date
        self.running_date = running_date
        self.calibration_starting_date = calibration_starting_date
        self.calibration_running_date = calibration_running_date

        self.freqly_return_pkl_filename_suffix=freqly_return_pkl_filename_suffix
        self.aggregated_pkl_file_suffix=aggregated_pkl_file_suffix
        self.aggregated_pkl_mapping_file_suffix=aggregated_pkl_mapping_file_suffix
        self.underlying = underlying
        self.list_pkl_file_suffix = list_pkl_file_suffix
        self.frequence=frequence
        self.algo=algo
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
        self.add_turn_over = add_turn_over
        self.skipping_size = skipping_size
        self.signals_list = napoleon_connector.load_pickled_list(local_root_directory=self.local_root_directory,
                                                                 list_pkl_file_name=self.list_pkl_file_name)

        self.signals_list = list(self.signals_list)
        self.signals_list.sort()

        self.dates_stub = starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y')

        if self.frequence == 'daily':
            if self.delay == 0:
                self.saving_return_path = self.local_root_directory+self.underlying+ '_' + self.dates_stub + self.freqly_return_pkl_filename_suffix
            else :
                self.saving_return_path = f'{self.local_root_directory}{self.underlying}_{self.dates_stub}_{self.delay}{self.freqly_return_pkl_filename_suffix}'
        else :
            self.saving_return_path = self.local_root_directory+self.underlying+ '_' + self.dates_stub + self.freqly_return_pkl_filename_suffix


        self.recompute_all = recompute_all
        self.db_path_suffix = db_path_suffix
        if self.frequence == 'daily':
            self.db_path_name = launcher_utility.get_daily_database_name(user, frequence, underlying, algo, starting_date, running_date, delay, db_path_suffix)
        else:
            self.db_path_name = launcher_utility.get_database_name(user, frequence, underlying, algo, starting_date, running_date, db_path_suffix)

        # if not self.recompute_all:
        #     saver = signal_result_analyzer.ParallelRunResultAnalyzer(drop_token=drop_token,
        #                                                              local_root_directory=local_root_directory, user=user,
        #                                                              db_path_name=self.db_path_name)
        #     self.precomputed_results_df, self.precomputed_signals_df = saver.analyzeAllRunResults()
        # else:
        #     self.precomputed_results_df, self.precomputed_signals_df  = None, None
        print('prereading data from '+self.db_path_name )
        saver = signal_result_analyzer.ParallelRunResultAnalyzer(drop_token=drop_token,
                                                                 local_root_directory=local_root_directory, user=user,
                                                                 db_path_name=self.db_path_name)
        self.precomputed_results_df, self.precomputed_signals_df = saver.analyzeAllRunResults()
        self.daily_ia_lookback_window = daily_ia_lookback_window


        print('done')

    @abstractmethod
    def runTrial(self,saver):
        pass

class AggregatingSignalRunner(AbstractRunner):
    def backup_to_dropbox(self):
        local_root_directory = Path(self.local_root_directory)
        aggregated_csv_file_name = self.aggregated_pkl_file_name.replace('pkl', 'csv')
        aggregated_csv_mapping_file_name = self.aggregated_pkl_mapping_file_name.replace('pkl', 'csv')

        aggregated_df = pd.read_pickle(local_root_directory / self.aggregated_pkl_file_name)
        aggregated_mapping_df = pd.read_pickle(local_root_directory / self.aggregated_pkl_mapping_file_name)

        aggregated_csv_full_path = local_root_directory / aggregated_csv_file_name
        aggregated_csv_mapping_full_path = local_root_directory / aggregated_csv_mapping_file_name

        aggregated_df.to_csv(aggregated_csv_full_path)
        aggregated_mapping_df.to_csv(aggregated_csv_mapping_full_path)
        print('backuping to dropbox '+str(aggregated_csv_full_path))
        self.dbx.upload(fullname=aggregated_csv_full_path, folder='', subfolder='', name=aggregated_csv_file_name,overwrite=True)
        print('backuping to dropbox '+str(aggregated_csv_mapping_full_path))
        self.dbx.upload(fullname=aggregated_csv_mapping_full_path, folder='', subfolder='',name=aggregated_csv_mapping_file_name, overwrite=True)


    def runSingleTrial(self, me_signal):
        try:
            print('Launching ' + me_signal)
            # we have to reload the file each time
            freqly_df = pd.read_pickle(self.saving_return_path)
            freqly_df = freqly_df.sort_index()
            print('time range before filtering ')
            print(max(freqly_df.index))
            print(min(freqly_df.index))
            freqly_df = freqly_df[freqly_df.index >= self.starting_date]
            freqly_df = freqly_df[freqly_df.index <= self.running_date]
            print('time range after filtering ')
            print(max(freqly_df.index))
            print(min(freqly_df.index))

            ## idiosyncratic run itself
            run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
            params = json.loads(run_json_string)
            signal_type = params['signal_type']
            normalization = params['normalization']
            trigger = params['trigger']
            transaction_costs = params['transaction_costs']

            if normalization and not signal_generator.is_signal_continuum(signal_type):
                return

            print('Launching computation with parameters : ' + run_json_string)

            if signal_type == 'long_only':
                freqly_df['signal'] = 1.
            else:
                lookback_window = params['lookback_window']
                if self.skipping_size < lookback_window:
                    raise Exception('The skipping size must be greater than the lookback window')
                # kwargs = {**generics, **idios}
                signal_generation_method_to_call = getattr(signal_generator, signal_type)
                freqly_df = signal_utility.roll_wrapper(freqly_df, lookback_window, self.skipping_size,
                                                        lambda x: signal_generation_method_to_call(data=x, **params),
                                                        trigger)
                freqly_df, _ = signal_utility.reconstitute_signal_perf(data=freqly_df,
                                                                       transaction_cost=transaction_costs,
                                                                       normalization=normalization)

            if self.add_turn_over:
                cumulated_signals = freqly_df[['close', 'signal', 'turn_over']].copy()
                cumulated_signals = cumulated_signals.rename(
                    columns={'signal': me_signal, 'turn_over': 'turn_over' + me_signal})
            else:
                cumulated_signals = freqly_df[['close', 'signal']].copy()
                cumulated_signals = cumulated_signals.rename(columns={'signal': me_signal})


            print('diiscretizing the signal ')
            return cumulated_signals
        except Exception as e:
            print('cannot compute ', me_signal)
            print(e)
            return None


    def runTrial(self, saver):
        cumulated_signals = None
        print('Number of signals to aggregate '+str(len(self.signals_list)))
        counter = 1
        mapping_dictionary = {}
        for me_signal in self.signals_list:
            # we have to reload the file each time
            freqly_df = pd.read_pickle(self.saving_return_path)
            freqly_df = freqly_df.sort_index()
            print('time range before filtering ')
            print(max(freqly_df.index))
            print(min(freqly_df.index))
            freqly_df = freqly_df[freqly_df.index >= self.starting_date]
            freqly_df = freqly_df[freqly_df.index <= self.running_date]
            print('time range after filtering ')
            print(max(freqly_df.index))
            print(min(freqly_df.index))
            close_df = freqly_df.copy()

            ## idiosyncratic run itself
            run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
            params = json.loads(run_json_string)
            signal_type = params['signal_type']
            normalization = params['normalization']
            trigger = params['trigger']
            transaction_costs = params['transaction_costs']

            if normalization and not signal_generator.is_signal_continuum(signal_type):
                return
            signal_column = 'signal'+str(counter)
            mapping_dictionary[me_signal]=[signal_column]
            if self.recompute_all:
                print('Launching computation with parameters : '+run_json_string)
                print('Signal number '+str(counter))
                # try:
                #     testing_presence_df = self.precomputed_results_df[me_signal]
                # except KeyError:
                #     print('cannot read ', me_signal)
                #     continue

                if signal_type == 'long_only':
                    freqly_df['signal']=1.
                else:
                    lookback_window = params['lookback_window']
                    if self.skipping_size < lookback_window:
                        raise Exception('The skipping size must be greater than the lookback window')
                    # kwargs = {**generics, **idios}
                    signal_generation_method_to_call = getattr(signal_generator, signal_type)
                    freqly_df = signal_utility.roll_wrapper(freqly_df, lookback_window, self.skipping_size,
                                              lambda x: signal_generation_method_to_call(data=x, **params), trigger)
                    freqly_df, _ = signal_utility.reconstitute_signal_perf(data = freqly_df, transaction_cost = transaction_costs, normalization = normalization)
            else :
                if self.add_turn_over:
                    raise Exception('to add turn over, you have to recompute all')
                try:
                    freqlyperf_df = self.precomputed_results_df[me_signal]
                except KeyError:
                    print('cannot read ', me_signal)
                    continue
                try:
                    freqlysig_df = self.precomputed_signals_df[me_signal]
                except KeyError:
                    print('cannot read ', me_signal)
                    continue
                freqlyperf_df = freqlyperf_df.to_frame()
                freqlyperf_df.columns = ['reconstituted_perf']
                freqlysig_df = freqlysig_df.to_frame()
                freqlysig_df.columns = ['signal']
                freqly_df = freqlyperf_df.merge(freqlysig_df, left_index = True, right_index = True)
                if cumulated_signals is None :
                    freqlyclose_df = close_df['close'].to_frame()
                    freqlyclose_df.columns = ['close']
                    freqly_df = freqly_df.merge(freqlyclose_df, left_index=True, right_index=True)
            if cumulated_signals is None:
                if self.add_turn_over:
                    cumulated_signals = freqly_df[['close','signal','turn_over']]
                    cumulated_signals = cumulated_signals.rename(columns={'signal': signal_column,'turn_over':'turn_over'+str(counter)})
                else :
                    cumulated_signals = freqly_df[['close','signal']]
                    cumulated_signals = cumulated_signals.rename(columns={'signal': signal_column})
            else :
                cumulated_signals[signal_column]=freqly_df['signal']
                if self.add_turn_over:
                    cumulated_signals['turn_over'+str(counter)]=freqly_df['turn_over']
            #freqly_df = freqly_df.drop(columns = ['signal','turn_over','reconstituted_perf','non_adjusted_perf_return','perf_return'])
            counter = counter + 1


        self.saving_cumulated_signals(cumulated_signals,mapping_dictionary)


    def saving_cumulated_signals(self, cumulated_signals_df, mapping_dictionary):
        print('discretizing the cumulated signals using ia')
        discrete_daily_signals = daily_bc_apply_standard_mean_discretization(signals_df=cumulated_signals_df, s=self.daily_ia_lookback_window)
        cumulated_signals_df['trend']=discrete_daily_signals
        print(f'discretization done {len(discrete_daily_signals)}')
        print('saving to ' + self.aggregated_pkl_file_name)
        cumulated_signals_df.to_pickle(self.local_root_directory + self.aggregated_pkl_file_name)
        print('saving to '+self.aggregated_pkl_mapping_file_name)
        pd.DataFrame(mapping_dictionary).to_pickle(self.local_root_directory + self.aggregated_pkl_mapping_file_name)







