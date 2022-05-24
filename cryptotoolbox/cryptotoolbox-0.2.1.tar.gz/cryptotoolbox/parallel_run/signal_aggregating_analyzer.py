
#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.signal import signal_generator
from cryptotoolbox.connector import crypto_connector
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.parallel_run import signal_result_analyzer
from cryptotoolbox.parallel_run import launcher_utility
import json

from pathlib import Path

class AggregatingSignalAnalyzer():
        def __init__(self, calibration_starting_date=None, calibration_running_date=None, starting_date=None, running_date=None,
                 drop_token=None, dropbox_backup=True, underlying=None, frequence='daily', selected_algo='', algo='',
                 freqly_return_pkl_filename_suffix='freqly_candels.pkl', aggregated_pkl_file_suffix='freqly_to_mix.pkl',
                 aggregated_pkl_mapping_file_suffix='freqly_to_mix_mapping.pkl', list_pkl_file_suffix='my_list.pkl',
                 local_root_directory='../data/', user='napoleon', add_turn_over=False, skipping_size=200,
                 recompute_all=True, db_path_suffix=None, daily_ia_lookback_window=21, delay = 0):
            super().__init__()
            self.starting_date = starting_date
            self.running_date = running_date
            self.calibration_starting_date = calibration_starting_date
            self.calibration_running_date = calibration_running_date

            self.freqly_return_pkl_filename_suffix = freqly_return_pkl_filename_suffix
            self.aggregated_pkl_file_suffix = aggregated_pkl_file_suffix
            self.aggregated_pkl_mapping_file_suffix = aggregated_pkl_mapping_file_suffix
            self.underlying = underlying
            self.list_pkl_file_suffix = list_pkl_file_suffix
            self.frequence = frequence
            self.algo = algo
            self.selected_algo = selected_algo

            self.calibrating_dates_stub = self.calibration_starting_date.strftime(
                '%d_%b_%Y') + '_' + self.calibration_running_date.strftime('%d_%b_%Y')
            self.dates_stub = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y')
            self.delay = delay

            if self.frequence == 'daily':
                self.list_pkl_file_name = self.calibrating_dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.list_pkl_file_suffix
                self.aggregated_pkl_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + '_' + str(self.delay) + self.aggregated_pkl_file_suffix
                self.aggregated_pkl_mapping_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + '_' + str(self.delay) + self.aggregated_pkl_mapping_file_suffix
            else:
                self.list_pkl_file_name = self.calibrating_dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.list_pkl_file_suffix
                self.aggregated_pkl_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.aggregated_pkl_file_suffix
                self.aggregated_pkl_mapping_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.aggregated_pkl_mapping_file_suffix

            self.local_root_directory = local_root_directory
            self.user = user
            self.dropbox_backup = dropbox_backup
            self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token, dropbox_backup=dropbox_backup)
            self.running_date = running_date
            self.starting_date = starting_date
            self.add_turn_over = add_turn_over
            self.skipping_size = skipping_size
            self.signals_list = napoleon_connector.load_pickled_list(local_root_directory=self.local_root_directory,
                                                                     list_pkl_file_name=self.list_pkl_file_name)

            self.signals_list = list(self.signals_list)
            self.signals_list.sort()

            self.dates_stub = starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y')
            self.saving_return_path = self.local_root_directory + self.underlying + '_' + self.dates_stub + self.freqly_return_pkl_filename_suffix

            self.recompute_all = recompute_all
            self.db_path_suffix = db_path_suffix

            if self.frequence == 'daily':
                self.db_path_name = launcher_utility.get_daily_database_name(user, frequence, underlying, algo,
                                                                             starting_date, running_date, delay,
                                                                             db_path_suffix)
            else:
                self.db_path_name = launcher_utility.get_database_name(user, frequence, underlying, algo, starting_date,
                                                                       running_date, db_path_suffix)

            # if not self.recompute_all:
            #     saver = signal_result_analyzer.ParallelRunResultAnalyzer(drop_token=drop_token,
            #                                                              local_root_directory=local_root_directory, user=user,
            #                                                              db_path_name=self.db_path_name)
            #     self.precomputed_results_df, self.precomputed_signals_df = saver.analyzeAllRunResults()
            # else:
            #     self.precomputed_results_df, self.precomputed_signals_df  = None, None

            if not self.recompute_all:
                print('prereading data from ' + self.db_path_name)
                saver = signal_result_analyzer.ParallelRunResultAnalyzer(drop_token=drop_token,
                                                                         local_root_directory=local_root_directory, user=user,
                                                                         db_path_name=self.db_path_name)
                self.precomputed_results_df, self.precomputed_signals_df = saver.analyzeAllRunResults()
                self.daily_ia_lookback_window = daily_ia_lookback_window
            print('initialization done')


        def load_aggregated_results(self):
            print(f'reading results saved to {self.local_root_directory + self.aggregated_pkl_file_name}')
            cumulated_signals_df = pd.read_pickle(self.local_root_directory + self.aggregated_pkl_file_name)
            print(f'reading results saved to {self.local_root_directory + self.aggregated_pkl_mapping_file_name}')
            mapping_dictionary_df = pd.read_pickle(self.local_root_directory + self.aggregated_pkl_mapping_file_name)
            return cumulated_signals_df, mapping_dictionary_df

