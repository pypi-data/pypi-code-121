#!/usr/bin/env python
# coding: utf-8

import pandas as pd

import numpy as np
from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.utility import weights
from cryptotoolbox.rebalancing import allocation
from cryptotoolbox.rebalancing import crypto_signal_mixer
from cryptotoolbox.forecasting import forecasting_utility
from cryptotoolbox.mixing import mixing_utility


class CryptoSignalMixer():
    def  __init__(self, starting_date = None, running_date = None, optimization_starting_date = None, optimization_starting_date_list=None, drop_token=None, dropbox_backup = True, save_model=False, supervision_npy_file_suffix='_supervision.npy', macro_supervision_npy_file_suffix='_macro_supervision.npy', features_saving_suffix='_features.npy', features_names_saving_suffix='_features_names.npy', daily_hourly_returns_pkl_file_suffix='_hourly_returns.pkl', hourly_returns_pkl_file_suffix='_daily_hourly_returns.pkl', local_root_directory='../data/', user = 'napoleon', n_start = 252, transaction_costs = None, crypto_ticker = None, strategies = None, underlyings = None, add_daily_hourlyzed=True,hourly_crypto_product_codes=None, daily_crypto_product_codes=None):
        super().__init__()
        self.supervision_npy_file_suffix = supervision_npy_file_suffix
        self.macro_supervision_npy_file_suffix = macro_supervision_npy_file_suffix
        self.features_saving_suffix = features_saving_suffix
        self.features_names_saving_suffix=features_names_saving_suffix
        self.hourly_returns_pkl_file_suffix=hourly_returns_pkl_file_suffix
        self.daily_hourly_returns_pkl_file_suffix = daily_hourly_returns_pkl_file_suffix
        self.local_root_directory=local_root_directory
        self.user=user
        self.n_start = n_start
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.save_model = save_model
        self.running_date = running_date
        self.starting_date = starting_date
        self.optimization_starting_date_list = optimization_starting_date_list
        self.optimization_starting_date = optimization_starting_date
        self.transaction_costs = transaction_costs
        self.crypto_ticker = crypto_ticker
        if self.crypto_ticker is not None:
            self.hourly_returns_pkl_file_name =  self.crypto_ticker + '_' + self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.hourly_returns_pkl_file_suffix
            self.daily_hourly_returns_pkl_file_name =  self.crypto_ticker + '_' + self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.daily_hourly_returns_pkl_file_suffix
        else :
            self.hourly_returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.hourly_returns_pkl_file_suffix
            self.daily_hourly_returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.daily_hourly_returns_pkl_file_suffix

        self.strategies = strategies
        self.underlyings = underlyings
        self.add_daily_hourlyzed = add_daily_hourlyzed
        self.hourly_crypto_product_codes  = hourly_crypto_product_codes
        self.daily_crypto_product_codes  = daily_crypto_product_codes

    def runTrial(self, saver, seed,  n, s, low_bound, up_bound, leverage, signal_type, idios_string):
        try:
            self.wrappedRunTrial(saver, seed, n, s, low_bound, up_bound, leverage, signal_type, idios_string)
        except Exception as e:
            print('################# : To investigate and relaunch')
            print(e)

    def wrappedRunTrial(self, saver, seed,  n, s, low_bound, up_bound, leverage, signal_type, idios_string):
        saving_key, idios = saver.create_saving_key(seed, n, s, low_bound, up_bound, leverage,signal_type, idios_string)

        check_run_existence, table_number = saver.checkRunExistence(saving_key)
        if check_run_existence:
            return

        print('Launching computation with parameters : '+saving_key)
        hourly_df = pd.read_pickle(self.local_root_directory + self.hourly_returns_pkl_file_name)
        daily_hourly_df = pd.read_pickle(self.local_root_directory + self.daily_hourly_returns_pkl_file_name)
        underlyings_df = daily_hourly_df[self.underlyings].copy()
        daily_hourly_df = daily_hourly_df.drop(columns = self.underlyings)
        hourly_df = hourly_df.drop(columns=self.underlyings)

        if len(self.hourly_crypto_product_codes) > 0:
            print('filtering')
            columns_to_keep = []
            for col in hourly_df.columns:
                for hourly_product_code in self.hourly_crypto_product_codes:
                    if hourly_product_code in col:
                        columns_to_keep.append(col)
            hourly_df = hourly_df[columns_to_keep].copy()


        if self.add_daily_hourlyzed and len(self.daily_crypto_product_codes)>0:
            print('filtering')
            print('filtering')
            columns_to_keep = []
            for col in daily_hourly_df.columns:
                for daily_product_code in self.daily_crypto_product_codes:
                    if daily_product_code in col:
                        columns_to_keep.append(col)
            daily_hourly_df = daily_hourly_df[columns_to_keep].copy()

        if self.add_daily_hourlyzed:
            print(f'merging {underlyings_df.shape} {hourly_df.shape} {daily_hourly_df.shape} ')
            hourly_df = hourly_df.filter(regex='^sig', axis=1).copy()
            daily_hourly_df = daily_hourly_df.filter(regex='^sig', axis=1).copy()
            print(f'merging {underlyings_df.shape} {hourly_df.shape} {daily_hourly_df.shape} ')
            df = pd.merge(hourly_df, daily_hourly_df, right_index=True, left_index=True)
            df = pd.merge(df, underlyings_df, right_index=True, left_index=True)
        else:
            df = hourly_df.copy()
            df = pd.merge(df, underlyings_df, right_index=True, left_index=True)


        if 'Date' in df.columns:
            print(df.columns)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

        df = df.fillna(method='ffill')
        df = df[df.index >= self.starting_date]
        print('max before filtering ' + str(max(df.index)))
        df = df[df.index <= self.running_date]

        print('max after filtering ' + str(max(df.index)))


        model = mixing_utility.instantiate_model(method=signal_type, idios = idios)

        # Compute rolling weights
        if self.optimization_starting_date_list is None:
            weights_df, portfolio = crypto_signal_mixer.rolling_mixing(
                model=signal_type,
                data_df=df,
                strategies=self.strategies,
                underlyings=self.underlyings,
                n=n,
                s=s,
                low_bound=low_bound,
                up_bound=up_bound,
                leverage = leverage,
                s_eval = None,
                calibration_step = None,
                optimization_starting_date=self.optimization_starting_date,
                transaction_costs=self.transaction_costs)
        else :
            weights_df, portfolio = crypto_signal_mixer.rolling_mixing_multistart(
                model=signal_type,
                data_df=df,
                strategies=self.strategies,
                underlyings=self.underlyings,
                n=n,
                s=s,
                low_bound=low_bound,
                up_bound=up_bound,
                leverage=leverage,
                s_eval=None,
                calibration_step=None,
                optimization_starting_date_list=self.optimization_starting_date_list,
                transaction_costs=self.transaction_costs)
            print('what do we do')



        print(weights_df.shape)
        print('onde')

        saver.saveResults(saving_key, portfolio, weights_df)