#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd

import numpy as np

from cryptotoolbox.utility import metrics
from cryptotoolbox.file_saver import dropbox_file_saver
from scipy.optimize import Bounds, LinearConstraint, minimize
from functools import partial

import torch


def f_minVar(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    transaction_costs =np.dot(abs(w - previous_w) , cost_parameters)

    mat_cov = np.cov(X, rowvar=False)
    w = w.reshape([N_, 1])
    to_minimize = np.sqrt(w.T @ mat_cov[assets][:, assets] @ w)
    return to_minimize + transaction_costs


def f_maxMean(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    transaction_costs =np.dot(abs(w - previous_w) , cost_parameters)
    w = w.reshape([N_, 1])
    to_minimize = - np.mean(np.cumprod(X[:, assets] @ w + 1, axis=0)[-1, :])
    return to_minimize + transaction_costs

def f_MeanVar(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    transaction_costs =np.dot(abs(w - previous_w) , cost_parameters)
    mat_cov = np.cov(X, rowvar=False)
    w = w.reshape([N_, 1])
    std_dev = np.sqrt(w.T @ mat_cov[assets][:, assets] @ w)
    mean_ret = np.mean(np.cumprod(X[:, assets] @ w + 1, axis=0)[-1, :])
    rebal_length = X.shape[0]
    to_minimize = np.sqrt(252) * std_dev - (np.float_power(mean_ret, rebal_length / 252) - 1)
    return to_minimize + transaction_costs

def f_sharpe(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    w = w.reshape([N_, 1])
    return  - metrics.sharpe(np.cumprod(np.prod(X[:, assets] @ w + 1 - (cost_parameters@abs(w-previous_w)), axis=1)))

def f_calmar(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    w = w.reshape([N_, 1])
    return - metrics.calmar(np.cumprod(np.prod(X[:, assets] @ w + 1 - (cost_parameters@abs(w-previous_w)), axis=1)))

def f_drawdown(assets, X, previous_w, cost_parameters, w):
    N_ = assets.sum()
    transaction_costs =np.dot(abs(w - previous_w) , cost_parameters)
    w = w.reshape([N_, 1])
    to_minimize = metrics.drawdown(np.cumprod(np.prod(X[:, assets] @ w + 1, axis=1))).max()
    return to_minimize + transaction_costs

class AbstractAssembler(ABC):
    def __init__(self, starting_date=None, running_date = None, drop_token=None, dropbox_backup = True, features_pkl_file_suffix='_features.pkl', macro_features_directory='features_macro', returns_pkl_file_suffix='_returns.pkl', local_root_directory='../data/', user='napoleon',
                 supervision_npy_file_suffix='_supervision.npy', macro_supervision_npy_file_suffix='_macro_supervision.npy', transaction_costs = None, crypto_ticker = None):
        super().__init__()

        self.features_pkl_file_suffix = features_pkl_file_suffix
        self.returns_pkl_file_suffix = returns_pkl_file_suffix

        if features_pkl_file_suffix is not None:
            self.features_pkl_file_name = running_date.strftime('%d_%b_%Y')+features_pkl_file_suffix
        else :
            self.features_pkl_file_name = None

        self.macro_features_directory=macro_features_directory
        self.local_root_directory = local_root_directory
        self.user = user
        self.supervision_npy_file_suffix = supervision_npy_file_suffix
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.macro_supervision_npy_file_suffix=macro_supervision_npy_file_suffix
        self.dropbox_backup = dropbox_backup
        self.running_date = running_date
        self.starting_date = starting_date
        self.transaction_costs = transaction_costs

        self.crypto_ticker = crypto_ticker
        if self.crypto_ticker is not None:
            self.returns_pkl_file_name =  self.crypto_ticker + '_' +self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix
        else :
            self.returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix

    @abstractmethod
    def computeUtility(self, s):
        pass


class UtilitySuperviser(AbstractAssembler):


    def computeUtility(self, rebal=10,low_bound=0.02, up_bound=0.4, cutting_rate_threshold=0.7):
        df = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder='', returns_pkl_file_name=self.returns_pkl_file_name, local_root_directory = self.local_root_directory)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        strats = [col for col in list(df.columns) if col != 'Date']

        print('size return '+str(df.shape))


        advanced_features = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder=self.macro_features_directory, returns_pkl_file_name=self.features_pkl_file_name, local_root_directory = self.local_root_directory)
        features_names = [col for col in list(advanced_features.columns) if col!='Date']
        advanced_features['Date'] = pd.to_datetime(advanced_features['Date'])

        max_date = max(advanced_features['Date'])
        print('Maximum features date '+str(max_date))
        print('size advanced_features '+str(advanced_features.shape))

        print('Maximum return running date before filter '+str(max(df.index)))
        df=df[df.index>=self.starting_date]
        df=df[df.index<=self.running_date]
        df = df.fillna(method='ffill')
        print('Maximum return running date after filter '+str(max(df.index)))
        print('Returns size')
        print(df.shape)

        np.random.seed(0)
        torch.manual_seed(0)
        ##===================##
        ##  Setting targets  ##
        ##===================##

        df_bis = df.copy()

        print('merging with advanced features')
        df_bis = pd.merge(df_bis, advanced_features, how='left', on=['Date'])

        print('merging done')
        df_bis.index = df_bis['Date']
        df_bis = df_bis.drop(columns=['Date'])
        print('return')

        df_bis = df_bis.fillna(method='ffill').fillna(method='bfill')
        # df_ret = df_bis.pct_change().fillna(0.)
        df_ret = df_bis.copy()

        print('Final returns size after merge with features')
        print(df_ret.shape)

        for col in strats:
            print(col + str(len(df_bis.columns)))
            df_ret[col] = df_bis[col].pct_change().fillna(0.)

        print('return done')
        print('return computed')

        ret_df = df_ret[strats]
        ret = ret_df.values


        T = df.index.size
        N = df.columns.size
        w0 = np.ones([N]) / N
        w_ = w0
        previous_w_dic = {}
        previous_w_dic['f_minVar']   = w_.copy()
        previous_w_dic['f_maxMean']  = w_.copy()
        previous_w_dic['f_MeanVar']  = w_.copy()
        previous_w_dic['f_sharpe']   = w_.copy()
        previous_w_dic['f_calmar']   = w_.copy()
        previous_w_dic['f_drawdown'] = w_.copy()

        # print('saving df_ret')
        # df_ret.to_pickle('../data/df_ret.pkl')

        print("recomputing supervision weights")
        # Set constraints and minimze

        utility_size = 6
        result = np.zeros([T, N, utility_size], np.float64)

        def process(series):
            # True if less than 50% of obs. are constant
            return series.value_counts(dropna=False).max() < cutting_rate_threshold * rebal

        if self.transaction_costs is None:
            print('no transaction costs given')
            costs_parameters = np.zeros(len(ret_df.columns))
        else:
            def get_fees_rate(asset, transaction_costs_dic):
                try:
                    fees = transaction_costs_dic[asset]
                except KeyError as e:
                    print(e)
                    return 0.
                return fees
            costs_parameters = np.fromiter(map(lambda x: get_fees_rate(x, self.transaction_costs), ret_df.columns), dtype=np.float64)

        # for t in range(max(n_past_features, s), T - s):
        for t in range(rebal, T):
            np.random.seed(0)
            torch.manual_seed(0)
            if t % 500 == 0:
                print('{:.2%}'.format(t / T))
            # we compute the utility output to predict only if not in future
            if t + rebal <= T:
                t_s = min(t + rebal, T)
                X = ret[t: t_s, :]
                # Avoid constant assets
                sub_X = ret_df.iloc[t: t_s, :].copy()
                assets = sub_X.apply(process).values
                N_ = assets.sum()
                if N_ != 0:
                    # Set constraints
                    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
                    up_bound_ = max(up_bound, 1 / N_)
                    low_bound_ = min(low_bound, 1 / N_)
                    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
                    # Search optimal weights => target
                    f_list = ['f_minVar', 'f_maxMean', 'f_sharpe', 'f_MeanVar', 'f_calmar', 'f_drawdown']
                    i = 0
                    for f in f_list:
                        previous_w_ = previous_w_dic[f]
                        np.random.seed(0)
                        torch.manual_seed(0)

                        func_to_optimize = partial(eval(f), assets, X, previous_w_[assets], costs_parameters[assets])
                        # Optimize f
                        w__ = minimize(
                            func_to_optimize,
                            previous_w_[assets],
                            method='SLSQP',
                            constraints=[const_sum],
                            bounds=const_ind
                        ).x

                        if np.isnan(w__.sum()):
                            print('Trouble converging : investigate')
                            w__ = previous_w_[assets]

                        w_[assets] = w__
                        w_[~assets] = 0.
                        s_w = w_.sum()

                        if s_w == 1.:
                            next_w = w_
                        elif s_w != 0.:
                            next_w = w_ / s_w
                        else:
                            next_w = w0
                        result[t: t + 1, :, i] = next_w
                        previous_w_dic[f] = next_w
                        i += 1


                else:
                    for ii in range(utility_size):
                        result[t: t + 1, :, ii] = w0


        print('saving localy file')
        print(np.isnan(result).sum(axis=0).sum())
        print(np.isinf(result).sum(axis=0).sum())
        if np.isnan(result).sum(axis=0).sum() > 0:
            raise Exception('trouble : nan in supervised output')
        if np.isinf(result).sum(axis=0).sum() > 0:
            raise Exception('trouble : nan in supervised output')

        print('final supervision shape '+ str(result.shape))
        self.dbx.local_supervision_npy_save_and_upload(starting_date= self.starting_date, ending_date = self.running_date, data = result, rebal = rebal , lower_bound= low_bound, upper_bound= up_bound,  local_root_directory= self.local_root_directory, user = self.user, supervision_npy_file_suffix= self.supervision_npy_file_suffix)
        print('files saved and updated to dropbox')






