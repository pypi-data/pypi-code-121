#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod
from cryptotoolbox.file_saver import dropbox_file_saver
import talib as ta
import numpy as np

import torch

from cryptotoolbox.features import features_type
from os import walk
import pandas as pd
from pathlib import Path

import decimal

from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import make_forecasting_frame
from tsfresh.utilities.dataframe_functions import impute

def buildAdvancedPriceFeatures(quotes_df=None, lookback_window=20, rolling_direction=1):
    strats = [col for col in quotes_df.columns if col != 'Date' ]
    aggregated_features = None
    for strat in strats:
        print('processing '+strat)
        df_shift, y = make_forecasting_frame(quotes_df[strat], kind="price", max_timeshift=lookback_window, rolling_direction=1)
        X = extract_features(df_shift, column_id="id", column_sort="time", column_value="value", impute_function=impute, show_warnings=False)
        X = X.loc[:, X.apply(pd.Series.nunique) != 1]
        X.columns = [strat + col for col in X.columns]
        if aggregated_features is None :
            aggregated_features = X
        else :
            aggregated_features = pd.merge(aggregated_features, X, how = 'left', left_index=True, right_index=True)
    aggregated_features['Date'] = quotes_df['Date']
    return aggregated_features



class AbstractAssembler(ABC):
    def __init__(self, starting_date = None, running_date=None, drop_token=None, dropbox_backup=True, returns_pkl_file_suffix='_returns.pkl', features_pkl_file_suffix='_features.pkl', ts_features_pkl_file_suffix='tsfresh_features.pkl', features_saving_suffix='_features.npy', features_names_saving_suffix='_features_names.npy',shortcut_features_saving_suffix='_shortcut_features.npy', shortcut_features_names_saving_suffix='_shortcut_features_names.npy',shortcut_features_pkl_file_name = 'shortcut.pkl', local_root_directory='../data/', user='napoleon',macro_features_directory = 'features_macro', rolling_direction=1, crypto_ticker = None):
        super().__init__()
        self.local_root_directory = local_root_directory
        self.user = user
        self.features_pkl_file_suffix = features_pkl_file_suffix
        self.returns_pkl_file_suffix = returns_pkl_file_suffix
        self.ts_features_pkl_file_suffix = ts_features_pkl_file_suffix

        self.features_saving_suffix = features_saving_suffix
        self.features_names_saving_suffix = features_names_saving_suffix

        self.macro_features_directory = macro_features_directory
        self.shortcut_features_pkl_file_name = shortcut_features_pkl_file_name
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.running_date=running_date
        self.starting_date=starting_date
        self.rolling_direction = rolling_direction

        self.features_pkl_file_name = running_date.strftime('%d_%b_%Y')+features_pkl_file_suffix

        self.ts_features_pkl_file_name = running_date.strftime('%d_%b_%Y')+ts_features_pkl_file_suffix

        self.shortcut_features_saving_suffix = shortcut_features_saving_suffix
        self.shortcut_features_names_saving_suffix = shortcut_features_names_saving_suffix
        self.backup_intermediary = True
        self.short_feat_df_suffix = '_short_feat_df.pkl'
        self.adv_feat_df_before_merge_suffix = '_adv_feat_before_merge_df.pkl'
        self.adv_feat_df_raw_before_merge_suffix = '_adv_feat_raw_before_merge_df.pkl'
        self.adv_feat_df_suffix = '_adv_feat_df.pkl'
        self.ret_feat_df_suffix = '_ret_feat_df.pkl'
        self.truncating_features = False

        self.crypto_ticker = crypto_ticker
        if self.crypto_ticker is not None:
            self.returns_pkl_file_name =  self.crypto_ticker + '_' +self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix
        else :
            self.returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix

    @abstractmethod
    def assembleFeature(self, feature_type, n_past_features, tsfresh_lookback_window):
        pass


class FeaturesAssembler(AbstractAssembler):
    def reassembleAdvancedFeaturesForClusterization(self, feature_type, n_past_features, tsfresh_lookback_window, simple = True):
        if (feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED) and n_past_features is None:
            return
        if (feature_type is features_type.FeaturesType.STANDARD or feature_type is features_type.FeaturesType.STANDARD_ADVANCED) and n_past_features is not None:
            return
        print('feature_type' + str(feature_type))
        print('n_past_features' + str(n_past_features))


        np.random.seed(0)
        torch.manual_seed(0)

        advanced_features, advanced_features_names = self.preprocessFeatures()
        df, strats, strat_features_names = self.preprocessReturns(tsfresh_lookback_window)
        shortcut_df = self.preprocessShortcutFeatures()


        features_names = [col for col in list(advanced_features.columns) if col != 'Date']


        print(df.columns)
        print(df.shape)

        print(advanced_features.columns)
        print(advanced_features.shape)

        # Computationnal period (default 1 year)


        ##===================##
        ##  Setting targets  ##
        ##===================##


        print('merging')
        df_ret = pd.merge(df, advanced_features, how='left', on=['Date'])

        df_ret = df_ret.replace([np.inf, -np.inf], np.nan)
        df_ret=df_ret.fillna(0.)

        print('number of infs in advanced features')
        print(np.isinf(df_ret[features_names]).sum(axis=0))

        print('number of infs in returns')
        print(np.isinf(df_ret[strats]).sum(axis=0))

        print('number of nans in advanced features')
        print(np.isnan(df_ret[features_names]).sum(axis=0))

        print('number of nans in returns')
        print(np.isnan(df_ret[strats]).sum(axis=0))

        if simple:
            return strats, strat_features_names, features_names, df_ret


        ret_df = df_ret[strats]
        ret = ret_df.values

        feat = df_ret[strat_features_names + features_names].values

        T = df.index.size
        N = len(strats)

        all_features_length = len(features_names) + len(strat_features_names)

        if feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
            features = np.zeros([T, n_past_features, N + all_features_length], np.float32)
            predictor_names = strats  + features_names + strat_features_names

        if feature_type is features_type.FeaturesType.HISTORY:
            features = np.zeros([T, n_past_features, N], np.float32)


        if feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
            for t in range(n_past_features, T):
                np.random.seed(0)
                torch.manual_seed(0)
                # the output to predict cannot be computed in the future
                # we still assemble the predictors
                # Set input data
                t_n = min(max(t - n_past_features, 0), T)
                F = feat[t_n: t, :]
                X_back = ret[t_n: t, :]

                if feature_type is features_type.FeaturesType.HISTORY_ADVANCED or feature_type is features_type.FeaturesType.HISTORY:
                    if feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
                        X_back = np.concatenate((X_back, F), axis=1)
                        predictor_names = features_names + strat_features_names
                    if feature_type is features_type.FeaturesType.HISTORY:
                        predictor_names = strats

                    features[t: t + 1] = X_back

                if t % 500 == 0:
                    print('{:.2%}'.format(t / T))
                # we compute the utility output to predict only if not in future
        else :
            if feature_type is features_type.FeaturesType.STANDARD_ADVANCED:

                #features = np.zeros([T, N + all_features_length], np.float32)
                features = feat
                predictor_names =  features_names + strat_features_names

            if feature_type is features_type.FeaturesType.STANDARD:
                #features = np.zeros([T, N], np.float32)
                features = ret
                predictor_names = strats

        return  predictor_names, features



    def preprocessMacroFeatures(self):
        macro_features_path = Path(self.local_root_directory+self.macro_features_directory)
        f = []
        for (dirpath, dirnames, filenames) in walk(macro_features_path):
            f.extend(filenames)
        all_merged_df = None
        for my_file in f:
            unpickled_df = pd.read_pickle(str(macro_features_path / my_file))
            unpickled_df.columns = [col.replace(' Index last quote', '').replace(' ', '_') for col in unpickled_df.columns]
            if all_merged_df is None:
                all_merged_df = unpickled_df
            else:
                all_merged_df = pd.merge(all_merged_df, unpickled_df, how='inner', left_index=True, right_index=True)

        all_merged_df['Date'] = all_merged_df.index
        all_merged_df['Date'] = pd.to_datetime(all_merged_df['Date'])
        macro_features = [col for col in list(all_merged_df.columns) if col!='Date']
        return all_merged_df, macro_features





    def preprocessFeatures(self):

        features = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder=self.macro_features_directory, returns_pkl_file_name=self.features_pkl_file_name, local_root_directory = Path(self.local_root_directory))
        if self.backup_intermediary :
            adv_feat_df_name = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.adv_feat_df_raw_before_merge_suffix
            print('saving '+adv_feat_df_name)
            features.to_pickle(self.local_root_directory+adv_feat_df_name)

        features_names = [col for col in list(features.columns) if col!='Date']
        features['Date'] = pd.to_datetime(features['Date'])


        # MM 3 mois
        for col in features_names:
            features["MM63_{}".format(col)] = features[col] / features[col].shift(1).rolling(window=63).mean() - 1
        # Z score 21 jours
        for col in features_names:
            features["Z_{}".format(col)] = (features[col] - features[col].rolling(window=21).mean()) / features[col].rolling(
                21).std()
        # Z score 63 jours
        for col in features_names:
            features["Z63_{}".format(col)] = (features[col].rolling(window=5).mean() - features[col].rolling(
                window=63).mean()) \
                                           / features[col].rolling(63).std()
        # MM 126 jours
        for col in features_names:
            features["MM126_{}".format(col)] = features[col] / features[col].shift(1).rolling(window=126).mean() - 1
        # MM 252 jours
        for col in features_names:
            features["MM252_{}".format(col)] = features[col] / features[col].shift(1).rolling(window=252).mean() - 1
        # MM 20 jours
        for col in features_names:
            features["MM20_{}".format(col)] = features[col] / features[col].shift(1).rolling(window=20).mean() - 1
        # ecart type:
        for col in features_names:
            features["vol20_{}".format(col)] = features[col].rolling(window=20).std() / features[col].rolling(
                window=20).mean()

        for col in features_names:
            features[col] = features[col].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.)

#        for col in features_names:
#            features[col] = (features[col] - features[col].mean()) / features[col].std(ddof=0)

        for col in features_names:
            features["quantile21_0_{}".format(col)] = features[col].rolling(window=20).quantile(0.)
            features["quantile21_25_{}".format(col)] = features[col].rolling(window=20).quantile(0.25)
            features["quantile21_50_{}".format(col)] = features[col].rolling(window=20).quantile(0.5)
            features["quantile21_55_{}".format(col)] = features[col].rolling(window=20).quantile(0.75)
            features["quantile21_75_{}".format(col)] = features[col].rolling(window=20).quantile(1.)

            features["quantile63_0_{}".format(col)] = features[col].rolling(window=63).quantile(0.)
            features["quantile63_25_{}".format(col)] = features[col].rolling(window=63).quantile(0.25)
            features["quantile63_50_{}".format(col)] = features[col].rolling(window=63).quantile(0.5)
            features["quantile63_55_{}".format(col)] = features[col].rolling(window=63).quantile(0.75)
            features["quantile63_75_{}".format(col)] = features[col].rolling(window=63).quantile(1.)

            features["quantile126_0_{}".format(col)] = features[col].rolling(window=126).quantile(0.)
            features["quantile126_25_{}".format(col)] = features[col].rolling(window=126).quantile(0.25)
            features["quantile126_50_{}".format(col)] = features[col].rolling(window=126).quantile(0.5)
            features["quantile126_55_{}".format(col)] = features[col].rolling(window=126).quantile(0.75)
            features["quantile126_75_{}".format(col)] = features[col].rolling(window=126).quantile(1.)

            features["quantile252_0_{}".format(col)] = features[col].rolling(window=252).quantile(0.)
            features["quantile252_25_{}".format(col)] = features[col].rolling(window=252).quantile(0.25)
            features["quantile252_50_{}".format(col)] = features[col].rolling(window=252).quantile(0.5)
            features["quantile252_55_{}".format(col)] = features[col].rolling(window=252).quantile(0.75)
            features["quantile252_75_{}".format(col)] = features[col].rolling(window=252).quantile(1.)

            features["mean_21_{}".format(col)] = features[col].rolling(window=21).mean()
            features["mean_63_{}".format(col)] = features[col].rolling(window=63).mean()
            features["mean_126_{}".format(col)] = features[col].rolling(window=126).mean()
            features["mean_252_{}".format(col)] = features[col].rolling(window=252).mean()

        features_names = [col for col in list(features.columns) if col!='Date']
        features['Date'] = pd.to_datetime(features['Date'])
        if self.truncating_features:
            def decimal_truncate(x):
                # By default rounding setting in python is decimal.ROUND_HALF_EVEN
                # decimal.getcontext().rounding = decimal.ROUND_DOWN
                c = decimal.Decimal(x)
                return float(round(c, 2))

            features = features.replace([np.inf, -np.inf], np.nan)
            for col in features_names:
                print('truncating '+col)
                features[col] = features[col].copy().apply(decimal_truncate)

        return features , features_names

    def preprocessShortcutFeatures(self):
        shortcut_df = self.dbx.local_overwrite_and_load_pickle(folder='', subfolder='',
                                                      returns_pkl_file_name=self.shortcut_features_pkl_file_name,
                                                      local_root_directory=self.local_root_directory)
        return shortcut_df

    def preprocessReturns(self, lookback_window, ts_fresh_indices = ['SPXT'], add_signal_predictor = False , add_ts_features_index = False):

        df = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder='', returns_pkl_file_name=self.returns_pkl_file_name, local_root_directory = self.local_root_directory)
        df['Date'] = pd.to_datetime(df['Date'])
        strats = [col for col in list(df.columns) if col != 'Date']
        df = df.set_index('Date')
        df = df.fillna(method='ffill').fillna(method='bfill')

        if add_signal_predictor:
            advanced_signals_ts_features = buildAdvancedPriceFeatures(quotes_df=df[strats], lookback_window=lookback_window,rolling_direction=self.rolling_direction)

        ts_features = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder=self.macro_features_directory, returns_pkl_file_name=self.ts_features_pkl_file_name, local_root_directory = Path(self.local_root_directory))

        ts_features_names = [col for col in list(ts_features.columns) if col!='Date']

        ts_features['Date'] = pd.to_datetime(ts_features['Date'])
        ts_features = ts_features.sort_values(by=['Date'])

        ts_features = ts_features.set_index('Date')
        ts_features=ts_features.astype('float64')

        print('Max ts fresh features date before advanced ' + str(max(ts_features.index)))
        print('Min ts fresh features date before advanced ' + str(min(ts_features.index)))
        if add_ts_features_index:
            advanced_ts_features = buildAdvancedPriceFeatures(quotes_df=ts_features[ts_fresh_indices],lookback_window=lookback_window, rolling_direction=self.rolling_direction)
            print('Advanced ts fresh features size')
            print(ts_features.shape)
            print('Max ts fresh features date ' + str(max(advanced_ts_features.index)))
            print('Min ts fresh features date ' + str(min(advanced_ts_features.index)))

            print('Advanced ts fresh features size')
            df = pd.merge(df, advanced_ts_features, how='left', left_index=True, right_index=True)

        print('Max return date after filtering' + str(max(df.index)))
        print('Min return date after filtering' + str(min(df.index)))

        for col in strats:
            df["ROC2_{}".format(col)] = df[col] / df[col].shift(2) - 1
        for col in strats:
            df["ROC3_{}".format(col)] = df[col] / df[col].shift(3) - 1
        for col in strats:
            df["ROC5_{}".format(col)] = df[col] / df[col].shift(5) - 1
        for col in strats:
            df["ROC10_{}".format(col)] = df[col] / df[col].shift(10) - 1
        for col in strats:
            df["ROC20_{}".format(col)] = df[col] / df[col].shift(20) - 1
        for col in strats:
            df["MM10_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=10).mean() - 1
        for col in strats:
            df["MM20_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=20).mean() - 1
        for col in strats:
            df["MM50_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=50).mean() - 1
        for col in strats:
            df["MM100_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=100).mean() - 1
        for col in strats:
            df["MM200_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=200).mean() - 1
        for col in strats:
            df["RSI14_{}".format(col)] = ta.RSI(df[col], 14) / 50 - 1
        for col in strats:
            df["RSI27_{}".format(col)] = ta.RSI(df[col], 27) / 50 - 1
        for col in strats:
            df["RSI44_{}".format(col)] = ta.RSI(df[col], 44) / 50 - 1
        for col in strats:
            df["MACD_{}".format(col)] = ta.MACD(df[col])[1]

        for col in strats:
            df["HL21_{}".format(col)] = (df[col] - df[col].shift(1).rolling(window=21).min()) / \
                                             (df[col].shift(1).rolling(window=21).max() - \
                                              df[col].shift(1).rolling(window=21).min()) * 2 - 1
        for col in strats:
            df["HL50_{}".format(col)] = (df[col] - df[col].shift(1).rolling(window=50).min()) / \
                                             (df[col].shift(1).rolling(window=50).max() - \
                                              df[col].shift(1).rolling(window=50).min()) * 2 - 1
        for col in strats:
            df["HL200_{}".format(col)] = (df[col] - df[col].shift(1).rolling(window=200).min()) / \
                                              (df[col].shift(1).rolling(window=200).max() - \
                                               df[col].shift(1).rolling(window=200).min()) * 2 - 1
        # MM 3 mois
        for col in strats:
            df["MM63_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=63).mean() - 1
        # Z score 21 jours
        for col in strats:
            df["Z_{}".format(col)] = (df[col] - df[col].rolling(window=21).mean()) / df[col].rolling(
                21).std()
        # Z score 63 jours
        for col in strats:
            df["Z63_{}".format(col)] = (df[col].rolling(window=5).mean() - df[col].rolling(
                window=63).mean()) \
                                           / df[col].rolling(63).std()
        # MM 126 jours
        for col in strats:
            df["MM126_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=126).mean() - 1
        # MM 252 jours
        for col in strats:
            df["MM252_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=252).mean() - 1
        # MM 20 jours
        for col in strats:
            df["MM20_{}".format(col)] = df[col] / df[col].shift(1).rolling(window=20).mean() - 1
        # ecart type:
        for col in strats:
            df["vol20_{}".format(col)] = df[col].rolling(window=20).std() / df[col].rolling(
                window=20).mean()

        print('computing returns')
        for col in strats:
            df[col] = df[col].pct_change().fillna(0.)

        for col in strats:
            df["quantile21_0_{}".format(col)] = df[col].rolling(window=20).quantile(0.)
            df["quantile21_25_{}".format(col)] = df[col].rolling(window=20).quantile(0.25)
            df["quantile21_50_{}".format(col)] = df[col].rolling(window=20).quantile(0.5)
            df["quantile21_55_{}".format(col)] = df[col].rolling(window=20).quantile(0.75)
            df["quantile21_75_{}".format(col)] = df[col].rolling(window=20).quantile(1.)

            df["quantile63_0_{}".format(col)] = df[col].rolling(window=63).quantile(0.)
            df["quantile63_25_{}".format(col)] = df[col].rolling(window=63).quantile(0.25)
            df["quantile63_50_{}".format(col)] = df[col].rolling(window=63).quantile(0.5)
            df["quantile63_55_{}".format(col)] = df[col].rolling(window=63).quantile(0.75)
            df["quantile63_75_{}".format(col)] = df[col].rolling(window=63).quantile(1.)

            df["quantile126_0_{}".format(col)] = df[col].rolling(window=126).quantile(0.)
            df["quantile126_25_{}".format(col)] = df[col].rolling(window=126).quantile(0.25)
            df["quantile126_50_{}".format(col)] = df[col].rolling(window=126).quantile(0.5)
            df["quantile126_55_{}".format(col)] = df[col].rolling(window=126).quantile(0.75)
            df["quantile126_75_{}".format(col)] = df[col].rolling(window=126).quantile(1.)

            df["quantile252_0_{}".format(col)] = df[col].rolling(window=252).quantile(0.)
            df["quantile252_25_{}".format(col)] = df[col].rolling(window=252).quantile(0.25)
            df["quantile252_50_{}".format(col)] = df[col].rolling(window=252).quantile(0.5)
            df["quantile252_55_{}".format(col)] = df[col].rolling(window=252).quantile(0.75)
            df["quantile252_75_{}".format(col)] = df[col].rolling(window=252).quantile(1.)

            df["mean_21_{}".format(col)] = df[col].rolling(window=21).mean()
            df["mean_63_{}".format(col)] = df[col].rolling(window=63).mean()
            df["mean_126_{}".format(col)] = df[col].rolling(window=126).mean()
            df["mean_252_{}".format(col)] = df[col].rolling(window=252).mean()

        strat_features = [col for col in list(df.columns) if col!='Date']
        return df , strats, strat_features


    def assembleFeature(self, feature_type, n_past_features, tsfresh_lookback_window):


        if (feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED) and n_past_features is None:
            return

        if (feature_type is features_type.FeaturesType.STANDARD or feature_type is features_type.FeaturesType.STANDARD_ADVANCED) and n_past_features is not None:
            return

        print('feature_type' + str(feature_type))
        print('n_past_features' + str(n_past_features))


        np.random.seed(0)
        torch.manual_seed(0)

        shortcut_features_df = self.preprocessShortcutFeatures()
        shortcut_features_names = [col for col in list(shortcut_features_df.columns) if col!='Date']


        df_ret, strats, strat_features_names = self.preprocessReturns(tsfresh_lookback_window)
        print('Max price date before filtering'+str(max(df_ret.index)))
        print('Min price date before filtering'+str(min(df_ret.index)))

        advanced_features, features_names = self.preprocessFeatures()

        max_date = max(advanced_features['Date'])
        min_date = min(advanced_features['Date'])
        print('Actual max feature date '+str(max_date))
        print('Actual ending date '+str(self.running_date))

        print('Actual min feature date '+str(min_date))
        print('Actual starting date '+str(self.starting_date))

        if self.backup_intermediary :
            adv_feat_df_name = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.adv_feat_df_before_merge_suffix
            print('saving '+adv_feat_df_name)
            advanced_features.to_pickle(self.local_root_directory+adv_feat_df_name)

        df_ret=df_ret[df_ret.index>=self.starting_date]
        df_ret=df_ret[df_ret.index<=self.running_date]

        print('Max price date '+str(max(df_ret.index)))
        print('Min price date '+str(min(df_ret.index)))


        print('Actual min shortcut feature date '+str(min(shortcut_features_df['Date'])))
        print('Actual max shortcut feature date '+str(max(shortcut_features_df['Date'])))

        shortcut_features_df = shortcut_features_df[shortcut_features_df['Date'] >= self.starting_date]
        shortcut_features_df = shortcut_features_df[shortcut_features_df['Date'] <= self.running_date]
        print('Max shortcut date '+str(max(shortcut_features_df['Date'])))
        print('Min shortcut date '+str(min(shortcut_features_df['Date'])))


        # quotes_df=quotes_df.sort_values(by='date', ascending=True)
        # quotes_df.head()

        print(df_ret.columns)
        print(df_ret.shape)

        print(advanced_features.columns)
        print(advanced_features.shape)

        # Computationnal period (default 1 year)


        ##===================##
        ##  Setting targets  ##
        ##===================##


        print('merging')
        df_ret = pd.merge(df_ret, advanced_features, how='left', on=['Date'])
        df_ret = pd.merge(df_ret, shortcut_features_df, how='left', on=['Date'])

        df_ret = df_ret.replace([np.inf, -np.inf], np.nan)
        df_ret=df_ret.fillna(0.)

        print('Final max predictor date ' + str(max(df_ret['Date'])))
        print('Predictors size')
        print(df_ret.shape)

        print('number of infs in advanced features')
        print(np.isinf(df_ret[features_names]).sum(axis=0))

        print('number of infs in shortcut features')
        print(np.isinf(df_ret[shortcut_features_names]).sum(axis=0))

        print('number of infs in returns')
        print(np.isinf(df_ret[strats]).sum(axis=0))

        print('number of nans in advanced features')
        print(np.isnan(df_ret[features_names]).sum(axis=0))

        print('number of nans in shortcut features')
        print(np.isnan(df_ret[shortcut_features_names]).sum(axis=0))

        print('number of nans in returns')
        print(np.isnan(df_ret[strats]).sum(axis=0))

        if self.backup_intermediary :
            short_feat_df_name = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.short_feat_df_suffix
            adv_feat_df_name = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.adv_feat_df_suffix
            ret_feat_df_name = self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.ret_feat_df_suffix
            print('saving '+short_feat_df_name)
            df_ret[shortcut_features_names].to_pickle(self.local_root_directory+short_feat_df_name)
            print('saving '+adv_feat_df_name)
            df_ret[features_names].to_pickle(self.local_root_directory+adv_feat_df_name)
            print('saving '+ret_feat_df_name)
            df_ret[strat_features_names].to_pickle(self.local_root_directory+ret_feat_df_name)


        ret_df = df_ret[strats]
        ret = ret_df.values

        feat = df_ret[strat_features_names + features_names].values

        T = df_ret.index.size
        N = len(strats)

        all_features_length = len(features_names) + len(strat_features_names)

        if feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
            features = np.zeros([T, n_past_features, N + all_features_length], np.float32)
            predictor_names = strats  + features_names + strat_features_names

        if feature_type is features_type.FeaturesType.HISTORY:
            features = np.zeros([T, n_past_features, N], np.float32)


        if feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
            for t in range(n_past_features, T):
                np.random.seed(0)
                torch.manual_seed(0)
                # the output to predict cannot be computed in the future
                # we still assemble the predictors
                # Set input data
                t_n = min(max(t - n_past_features, 0), T)
                F = feat[t_n: t, :]
                X_back = ret[t_n: t, :]

                if feature_type is features_type.FeaturesType.HISTORY_ADVANCED or feature_type is features_type.FeaturesType.HISTORY:
                    if feature_type is features_type.FeaturesType.HISTORY_ADVANCED:
                        X_back = np.concatenate((X_back, F), axis=1)
                        predictor_names = features_names + strat_features_names
                    if feature_type is features_type.FeaturesType.HISTORY:
                        predictor_names = strats


                    features[t: t + 1] = X_back

                if t % 500 == 0:
                    print('{:.2%}'.format(t / T))
                # we compute the utility output to predict only if not in future
        else :
            if feature_type is features_type.FeaturesType.STANDARD_ADVANCED:

                #features = np.zeros([T, N + all_features_length], np.float32)
                features = feat
                predictor_names =  features_names + strat_features_names

            if feature_type is features_type.FeaturesType.STANDARD:
                #features = np.zeros([T, N], np.float32)
                features = ret
                predictor_names = strats

        print('saving files')

        shortcut_features = df_ret[shortcut_features_names].values
        print('number of nan/infinity shortcut features')
        print(np.isnan(shortcut_features).sum(axis=0).sum())
        print(np.isinf(shortcut_features).sum(axis=0).sum())

        print('number of nan/infinity features')
        print(np.isnan(features).sum(axis=0).sum())
        print(np.isinf(features).sum(axis=0).sum())
        if np.isnan(features).sum(axis=0).sum() > 0:
            raise Exception('nan values for assembled features')
        if np.isinf(features).sum(axis=0).sum() > 0:
            raise Exception('inf values for assembled features')

        if np.isnan(features).sum(axis=0).sum() > 0:
            raise Exception('nan values for assembled features')
        if np.isinf(features).sum(axis=0).sum() > 0:
            raise Exception('inf values for assembled features')
        print('final size saved '+str(features.shape))
        self.dbx.local_features_npy_save_and_upload(starting_date = self.starting_date,ending_date = self.running_date, shortcut_features=shortcut_features, features = features,features_names= predictor_names, shortcut_features_names = shortcut_features_names, feature_type=feature_type, n_past_features = n_past_features , local_root_directory= self.local_root_directory, user = self.user, features_saving_suffix=self.features_saving_suffix, features_names_saving_suffix=self.features_names_saving_suffix, shortcut_features_saving_suffix=self.shortcut_features_saving_suffix, shortcut_features_names_saving_suffix=self.shortcut_features_names_saving_suffix)


