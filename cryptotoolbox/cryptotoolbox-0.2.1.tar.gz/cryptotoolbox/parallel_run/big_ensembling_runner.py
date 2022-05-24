#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd

import numpy as np
from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.utility import weights
from cryptotoolbox.rebalancing import allocation


class AbstractRunner(ABC):
    def __init__(self, starting_date = None, running_date = None, drop_token=None, dropbox_backup = True, save_model=False, supervision_npy_file_suffix='_supervision.npy', macro_supervision_npy_file_suffix='_macro_supervision.npy', features_saving_suffix='_features.npy', features_names_saving_suffix='_features_names.npy', returns_pkl_file_suffix='_returns.pkl', local_root_directory='../data/', user = 'napoleon', n_start = 252, transaction_costs = None, crypto_ticker = None):
        super().__init__()
        self.supervision_npy_file_suffix = supervision_npy_file_suffix
        self.macro_supervision_npy_file_suffix = macro_supervision_npy_file_suffix
        self.features_saving_suffix = features_saving_suffix
        self.features_names_saving_suffix=features_names_saving_suffix
        self.returns_pkl_file_suffix=returns_pkl_file_suffix


        self.local_root_directory=local_root_directory
        self.user=user
        self.n_start = n_start
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.save_model = save_model
        self.running_date = running_date
        self.starting_date = starting_date
        self.maximize_perf = True
        self.minimize_drawdown = True
        self.equaly_weighted = True
        self.erc_weighted = True
        self.ivp_allocation = True
        self.mvp_allocation = True
        self.hrp_allocation = True
        self.hrc_allocation = True
        self.mdp_allocation = True
        self.transaction_costs = transaction_costs
        self.crypto_ticker = crypto_ticker
        if self.crypto_ticker is not None:
            self.returns_pkl_file_name =  self.crypto_ticker + '_' + self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix
        else :
            self.returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix
    @abstractmethod
    def runTrial(self,saver, seed,  n, s, low_bound, up_bound, leverage):
        pass


class BigEnsemblingRunner(AbstractRunner):
    def runTrial(self, saver, seed,  n, s, low_bound, up_bound, leverage):
        try:
            self.wrappedRunTrial(saver, seed, n, s, low_bound, up_bound, leverage)
        except Exception as e:
            print('################# : To investigate and relaunch')
            print('################# : To investigate and relaunch')
            print('################# : To investigate and relaunch')
            print(e)

    def wrappedRunTrial(self, saver, seed,  n, s, low_bound, up_bound, leverage):

        mp_saving_key = saver.create_saving_key('mp_',seed,  n, s, low_bound, up_bound, leverage)
        dd_saving_key = saver.create_saving_key('dd_',seed,  n, s, low_bound, up_bound, leverage)
        ew_saving_key = saver.create_saving_key('ew_',seed,  n, s, low_bound, up_bound, leverage)
        erc_saving_key = saver.create_saving_key('erc_',seed,  n, s, low_bound, up_bound, leverage)
        ivp_saving_key = saver.create_saving_key('ivp_',seed,  n, s, low_bound, up_bound, leverage)
        mvp_saving_key = saver.create_saving_key('mvp_',seed,  n, s, low_bound, up_bound, leverage)
        hrp_saving_key = saver.create_saving_key('hrp_',seed,  n, s, low_bound, up_bound, leverage)
        hrc_saving_key = saver.create_saving_key('hrc_',seed,  n, s, low_bound, up_bound, leverage)
        mdp_saving_key = saver.create_saving_key('mdp_',seed,  n, s, low_bound, up_bound, leverage)


        print('Launching computation with parameters : '+mp_saving_key)

        df = pd.read_pickle(self.local_root_directory + self.returns_pkl_file_name)
        if 'Date' in df.columns:
            print(df.columns)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

        df = df.fillna(method='ffill')
        df = df[df.index >= self.starting_date]
        print('max before filtering ' + str(max(df.index)))
        df = df[df.index <= self.running_date]

        print('max after filtering ' + str(max(df.index)))
        ### getting the transaction costs
        df_res = df.copy()
        df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
        if self.transaction_costs is None:
            print('no transaction costs given')
            costs_parameters = np.zeros(len(df_ret.columns))
        else:
            def get_fees_rate(asset, transaction_costs_dic):
                try:
                    fees = transaction_costs_dic[asset]
                except KeyError as e:
                    print(e)
                    return 0.
                return fees

            if isinstance(self.transaction_costs,dict):
                costs_parameters = np.fromiter(map(lambda x: get_fees_rate(x, self.transaction_costs), df_ret.columns),
                                               dtype=np.float64)
            elif isinstance(self.transaction_costs,float):
                costs_parameters = np.ones(len(df_ret.columns)) * self.transaction_costs
            else:
                print('no transaction costs given')
                costs_parameters = np.zeros(len(df_ret.columns))

        check_maxperf_existence, _ = saver.checkRunExistence(mp_saving_key)
        if self.maximize_perf and not check_maxperf_existence:
            print('maximizing perf')

            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.maxPerf,
                df_res,
                n=n,
                s=s,
                normalize=True,
                low_bound=low_bound,
                up_bound=up_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )

            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(mp_saving_key, portfolio, weight_normalized,last_predicted_weights)




        check_drawdown_existence, _ = saver.checkRunExistence(dd_saving_key)
        if self.minimize_drawdown and not check_drawdown_existence:
            print('minimizing drawdown')
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.minDrawdown,
                df_res,
                n=n,
                s=s,
                normalize=True,
                low_bound=low_bound,
                up_bound=up_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(dd_saving_key, portfolio, weight_normalized,last_predicted_weights)

        check_ew_existence, _ = saver.checkRunExistence(ew_saving_key)
        if self.equaly_weighted and not check_ew_existence:
            print('equally weighted')
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(ew_saving_key, portfolio, weight_normalized,last_predicted_weights)


        check_erc_existence, _ = saver.checkRunExistence(erc_saving_key)
        if self.erc_weighted and not check_erc_existence:
            print('computing erc weights')
            df_res = df.copy()
            # Compute rolling weights
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.ERC,
                df_res,
                n=n,
                s=s,
                ret=False,
                low_bound=low_bound,
                up_bound=up_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(erc_saving_key, portfolio, weight_normalized,last_predicted_weights)


        check_ivp_existence, _ = saver.checkRunExistence(ivp_saving_key)
        if self.ivp_allocation and not check_ivp_existence:
            print('computing ivp weights')
            # Compute rolling weights
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.IVP,
                df_res,
                n=n,
                s=s,
                normalize=True,
                low_bound=low_bound,
                up_bound=up_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(ivp_saving_key, portfolio, weight_normalized,last_predicted_weights)



        check_mpv_existence, _ = saver.checkRunExistence(mvp_saving_key)
        if self.mvp_allocation and not check_mpv_existence:
            print('computing mvp weights')
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.MVP_uc,
                df_res,
                n=n,
                s=s,
                low_bound=low_bound,
                up_bound=up_bound,
                ret=False,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(mvp_saving_key, portfolio, weight_normalized,last_predicted_weights)


        check_hrp_existence, _ = saver.checkRunExistence(hrp_saving_key)
        if self.hrp_allocation and not check_hrp_existence:
            print('computing hrp weights')
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.HRP,
                df_res,
                n=n,
                s=s,
                ret=True,
                drift=True,
                method='centroid',
                metric='mse',
                up_bound=up_bound,
                low_bound=low_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(hrp_saving_key, portfolio, weight_normalized,last_predicted_weights)


        check_hrc_existence, _ = saver.checkRunExistence(hrc_saving_key)
        if self.hrc_allocation and not check_hrc_existence:
            print('computing hrc weights')
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.HRC,
                df_res,
                n=n,
                s=s,
                up_bound=up_bound,
                low_bound=low_bound,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(hrc_saving_key, portfolio, weight_normalized,last_predicted_weights)

        check_mdp_existence, _ = saver.checkRunExistence(mdp_saving_key)
        if self.mdp_allocation and not check_mdp_existence:
            print('computing mdp weights')
            # Compute rolling weights
            df_res = df.copy()
            portfolio, weight_mat = allocation.rolling_allocation(
                allocation.MDP,
                df_res,
                n=n,
                s=s,
                ret=False,
                drift=True,
                up_bound=up_bound,
                low_bound=low_bound,
                filtering_threshold=0.9,
                transaction_costs = costs_parameters
            )
            df_ret = df_res.fillna(method='bfill').pct_change().fillna(0).copy()
            weight_normalized, last_predicted_weights = weights.weights_shift(weight_mat=weight_mat)
            weight_normalized = weight_normalized*leverage

            #portfolio = np.cumprod(np.prod(df_ret * weight_normalized.values + 1, axis=1))
            # # Compute portfolio perf
            transaction_costs_matrix = abs(weight_normalized - weight_normalized.shift(1)) *costs_parameters
            adjusted_returns = df_ret * weight_normalized.values - transaction_costs_matrix
            portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
            saver.saveResults(mdp_saving_key, portfolio, weight_normalized,last_predicted_weights)
