#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.utility import metrics

from cryptotoolbox.signal import signal_generator
from cryptotoolbox.signal import signal_utility


class AbstractRunner(ABC):
    def __init__(self, starting_date = None, running_date = None, drop_token=None, dropbox_backup = True, underlying = None, freqly_pkl_file_name_suffix='freqly_candels.pkl', local_root_directory='../data/', user = 'napoleon',period=252):
        super().__init__()
        self.freqly_pkl_file_name_suffix=freqly_pkl_file_name_suffix
        self.underlying = underlying
        self.local_root_directory=local_root_directory
        self.dates_stub = starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime('%d_%b_%Y')
        self.saving_return_path = self.local_root_directory+self.underlying+ '_' + self.dates_stub + self.freqly_pkl_file_name_suffix
        self.user=user
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.running_date = running_date
        self.starting_date = starting_date
        self.period = period

    @abstractmethod
    def runTrial(self,saver,  seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator):
        pass

class SimpleSignalRunner(AbstractRunner):

    def runTrial(self, saver, seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator):
        try:
            self.mightBreakRunTrial(saver, seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator)
        except Exception as e:
            print(f'trouble {e} with run {(saver, seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator)}')
    def mightBreakRunTrial(self, saver, seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator):
        saving_key, idios = saver.create_saving_key(seed, trigger, signal_type, idios_string, transaction_costs, normalization, modulator)
        check_run_existence, table_number = saver.checkRunExistence(saving_key)
        exhaustive_check_run_existence, exhaustive_table_number = saver.exhaustiveCheckRunExistence(saving_key)
        assert check_run_existence == exhaustive_check_run_existence
        if check_run_existence:
            assert table_number == exhaustive_table_number
        if check_run_existence:
            return
        if normalization and not signal_generator.is_signal_continuum(signal_type):
            print('not normalizing a not continuous signal')
            return
        print('Launching computation with parameters : '+saving_key)
        print('loading returns '+self.saving_return_path)
        freqly_df = pd.read_pickle(self.saving_return_path)
        print('number of duplicated dates')
        print(freqly_df.index.duplicated().sum())
        freqly_df = freqly_df.sort_index()
        print('time range before filtering ')
        print(max(freqly_df.index))
        print(min(freqly_df.index))
        try:
            freqly_df = freqly_df[freqly_df.index >= self.starting_date]
            freqly_df = freqly_df[freqly_df.index <= self.running_date]
        except:
            freqly_df.index = pd.to_datetime(freqly_df.index)
            freqly_df = freqly_df[freqly_df.index >= self.starting_date]
            freqly_df = freqly_df[freqly_df.index <= self.running_date]
        print('time range after filtering ')
        print(max(freqly_df.index))
        print(min(freqly_df.index))
        if signal_type == 'long_only':
            freqly_df['signal']=1.
        else:
            lookback_window = idios['lookback_window']
            skipping_size = lookback_window
            # kwargs = {**generics, **idios}
            signal_generation_method_to_call = getattr(signal_generator, signal_type)
            try:
                freqly_df = signal_utility.roll_wrapper(freqly_df, lookback_window, skipping_size,
                                                        lambda x: signal_generation_method_to_call(data=x, **idios),
                                                        trigger)
            except Exception as inst:
                print('Trouble backtesting signal')
                print(inst)
                return
        freqly_df['signal'] = freqly_df['signal']*modulator

        freqly_df, _ = signal_utility.reconstitute_signal_perf(data = freqly_df, transaction_cost = transaction_costs , normalization = normalization)
        sharpe_strat = metrics.sharpe(freqly_df['perf_return'].dropna(), period= self.period, from_ret=True)
        sharpe_under = metrics.sharpe(freqly_df['close_return'].dropna(), period= self.period, from_ret=True)
        freqly_df = freqly_df.dropna()
        print('underlying sharpe')
        print(sharpe_under)
        print('strat sharpe')
        print(sharpe_strat)
        print('size before dropping duplicates')
        print(freqly_df.shape)
        freqly_df = freqly_df.drop_duplicates()
        print('size after dropping duplicates')
        print(freqly_df.shape)

        saver.saveAll(saving_key, freqly_df)
        print('save done')
        return






