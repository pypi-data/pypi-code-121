#!/usr/bin/env python3
# coding: utf-8

import sqlite3

from multiprocessing import Pool
from cryptotoolbox.file_saver import dropbox_file_saver

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.signal import signal_generator
from cryptotoolbox.connector import napoleon_connector
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.parallel_run import signal_result_analyzer
from cryptotoolbox.parallel_run import launcher_utility
import json
import pandas as pd

class RealTimeBacktestSignalEnsemblingParalleLauncher():
    def __init__(self, starting_date=None, running_date=None, drop_token='', dropbox_backup=True, local_root_directory='../data',underlying = None, frequence='daily', selected_algo='',user='napoleon',  db_path_suffix = '_run.sqlite', list_pkl_file_suffix = 'my_list.pkl',freqly_return_pkl_filename_suffix='freqly_candels.pkl'):
        self.starting_date = starting_date
        self.running_date = running_date
        self.args = []
        self.counter = 1
        self.seed = 0
        self.local_root_directory = local_root_directory

        self.underlying = underlying
        self.list_pkl_file_suffix = list_pkl_file_suffix
        self.frequence=frequence
        self.selected_algo=selected_algo
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.dates_stub = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y')

        self.list_pkl_file_name = self.dates_stub + '_' + self.underlying + '_' + self.frequence + '_' + self.selected_algo + self.list_pkl_file_suffix
        print('selected algos')
        print(self.list_pkl_file_name)
        if dropbox_backup:
            self.signals_list = self.dbx.download_pkl(pkl_file_name=self.list_pkl_file_name)
        else:
            self.signals_list = napoleon_connector.load_pickled_list(local_root_directory=self.local_root_directory,
                                                                 list_pkl_file_name=self.list_pkl_file_name)
        max_lookback_window = 0
        for me_signal in self.signals_list:
            self.args.append((me_signal))
            self.counter = self.counter + 1
            run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
            params = json.loads(run_json_string)
            if params['lookback_window']>max_lookback_window:
                max_lookback_window=params['lookback_window']
        self.max_lookback_window = max_lookback_window

        self.args.sort()
        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  user + db_path_suffix
        self.db_path = self.local_root_directory + self.filename
        self.runs = []
        self.totalRow = 0
        self.empty_runs_to_investigate = []
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.freqly_return_pkl_filename_suffix=freqly_return_pkl_filename_suffix
        self.saving_return_path = self.local_root_directory+self.underlying+self.freqly_return_pkl_filename_suffix
        freqly_df = pd.read_pickle(self.saving_return_path)
        print('number of duplicated dates')
        print(freqly_df.index.duplicated().sum())
        freqly_df = freqly_df.sort_index()
        print('time range before filtering ')
        print(max(freqly_df.index))
        print(min(freqly_df.index))
        # freqly_df = freqly_df[freqly_df.index >= self.starting_date]
        # freqly_df = freqly_df[freqly_df.index <= self.running_date]
        print('time range after filtering ')
        print(max(freqly_df.index))
        print(min(freqly_df.index))
        self.freqly_df = freqly_df

    def launchParallelPool(self, use_num_cpu):
        print('launching parallel computation for alphas at ')
        with Pool(processes=use_num_cpu) as pool:
            run_results = pool.starmap(self.runTrial, self.args)
        print('parallel computation done')
        print('results length')
        print(len(run_results))


    def launchSequential(self):
        print('launching sequential computation for alphas at ')
        run_results = []
        for meArg in self.args:
            run_results.append(self.runTrial(meArg))
        print('results length')
        print(len(run_results))


    def runTrial(self, me_signal):
        ## idiosyncratic run itself
        run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        params = json.loads(run_json_string)
        signal_type = params['signal_type']
        normalization = params['normalization']
        trigger = params['trigger']
        transaction_costs = params['transaction_costs']
        if normalization and not signal_generator.is_signal_continuum(signal_type):
            return

        lookback_window = params['lookback_window']
        signal_generation_method_to_call = getattr(signal_generator, signal_type)
        last_generated_signal = signal_utility.compute_last_signal(self.freqly_df, lookback_window,
                                                                   lambda x: signal_generation_method_to_call(
                                                                       data=x, **params))
        print('last_generated_signal')
        print(last_generated_signal)
        return last_generated_signal