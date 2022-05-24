#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from cryptotoolbox.neural_net import roll_multi_layer_lstm
from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.neural_net import roll_multi_layer_perceptron
from cryptotoolbox.boosted_trees import roll_lightgbm
from cryptotoolbox.features import features_type
from cryptotoolbox.utility import utility

import torch
import torch.nn as nn

class AbstractRunner(ABC):
    def __init__(self, starting_date = None, running_date = None, drop_token=None, dropbox_backup = True, supervision_npy_file_suffix='_supervision.npy', macro_supervision_npy_file_suffix='_macro_supervision.npy', features_saving_suffix='_features.npy', features_names_saving_suffix='_features_names.npy', returns_pkl_file_name='returns.pkl', shortcut_features_names_saving_suffix = '_shortcut_features_names.npy', shortcut_features_saving_suffix='_shortcut_features.npy', local_root_directory='../data/', user = 'napoleon', n_start = 252, maximum_precision=True, shortcut_features=False):
        super().__init__()
        self.supervision_npy_file_suffix=supervision_npy_file_suffix
        self.macro_supervision_npy_file_suffix=macro_supervision_npy_file_suffix
        self.features_saving_suffix=features_saving_suffix
        self.features_names_saving_suffix=features_names_saving_suffix
        self.returns_pkl_file_name=returns_pkl_file_name
        self.local_root_directory=local_root_directory
        self.shortcut_features_saving_suffix = shortcut_features_saving_suffix
        self.shortcut_features_names_saving_suffix = shortcut_features_names_saving_suffix
        self.shortcut_features = shortcut_features
        self.user=user
        self.n_start = n_start
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.starting_date = starting_date
        self.running_date = running_date
        self.maximum_precision = maximum_precision

    @abstractmethod
    def runTrial(self,saver, seed, sup, layers, epochs, n_past_features, n, s, whole_history, advance_feature, advance_signal,
                 normalize, activation_string, convolution, lr_start, lr_type, low_bound, up_bound):
        pass

class SimpleExplainer(AbstractRunner):
    def runTrial(self, saver, seed, sup, layers, epochs, n_past_features, n, s, feature_type, activation_type,
                 convolution, lr_start, lr_type, low_bound, up_bound):

        if (
                feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED) and n_past_features is None:
            return
        if (
                feature_type is features_type.FeaturesType.STANDARD or feature_type is features_type.FeaturesType.STANDARD_ADVANCED) and n_past_features is not None:
            return

        meArg = (
            seed, sup, layers, epochs, n_past_features, n, s, feature_type,
            activation_type, convolution, lr_start, lr_type, low_bound, up_bound)

        meArgList = list(meArg)
        meArgList = [str(it) for it in meArgList]
        savingKey = ''.join(meArgList)
        savingKey = savingKey.replace('[', '')
        savingKey = savingKey.replace(']', '')
        savingKey = savingKey.replace(',', '')
        savingKey = savingKey.replace(' ', '')
        savingKey = savingKey.replace('.', '')
        # savingKey = savingKey.replace('_','')
        savingKey = 'T_' + savingKey

        print('Launching computation with parameters : ' + savingKey)

        supervisors = {}
        supervisors['f_minVar'] = 0
        supervisors['f_maxMean'] = 1
        supervisors['f_sharpe'] = 2
        supervisors['f_MeanVar'] = 3
        supervisors['f_calmar'] = 4
        supervisors['f_drawdown'] = 5

        df = self.dbx.local_overwrite_and_load_pickle(folder='', subfolder='',
                                                      returns_pkl_file_name=self.returns_pkl_file_name,
                                                      local_root_directory=self.local_root_directory)

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df[df.index>=self.starting_date]
        df = df[df.index<=self.running_date]

        dates = df.index
        df = df.fillna(method='ffill')
        print('size return ' + str(df.shape))

        result = self.dbx.local_supervision_npy_overwrite_and_load_array(starting_date=self.starting_date, ending_date=self.running_date, rebal=s, lower_bound=low_bound,
                                                                         upper_bound=up_bound,
                                                                         local_root_directory=self.local_root_directory,
                                                                         user=self.user,
                                                                         supervision_npy_file_suffix=self.supervision_npy_file_suffix)

        np.random.seed(seed)
        torch.manual_seed(seed)
        # Set data
        whole_history = (
                    feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED)

        features, features_names, shortcut_features, shortcut_features_names = self.dbx.local_features_npy_ovverwrite_and_load_array(starting_date= self.starting_date, ending_date = self.running_date,feature_type=feature_type, n_past_features=n_past_features,
                                                    local_root_directory=self.local_root_directory, user=self.user,
                                                    features_saving_suffix=self.features_saving_suffix,
                                                    features_names_saving_suffix=self.features_names_saving_suffix,
                                                    shortcut_features_saving_suffix=self.shortcut_features_saving_suffix,
                                                    shortcut_features_names_saving_suffix=self.shortcut_features_names_saving_suffix)


        assert shortcut_features.shape[0] == features.shape[0]

        # the save files necessarily match the beginning date
        shortcut_features = shortcut_features[:len(df)]
        features = features[:len(df)]
        result = result[:len(df)]

        X = features[self.n_start:]
        y = result[self.n_start:, :, supervisors[sup]]
        df = df.iloc[self.n_start:]
        dates = dates[self.n_start:]

        print('predictors')
        print(X.shape)
        print('utility')
        print(y.shape)
        print('prices')
        print(df.shape)
        print('dates')
        print(len(dates))

        # convolution 0 : perceptron
        # convolution 1 : LSTM
        # convolution 2 : xgboost

        if whole_history:
            if convolution == 2:
                print('no whole time history with ensembling method')
                return
            if convolution == 0:
                print('no whole time history with multi layers perceptron')
                # uncomment if you want multi layers perceptron with full historical backtest
                # print('flattening predictor time series for perceptron')
                # _X = np.empty((X.shape[0], X.shape[1] * X.shape[2]), dtype=np.float32)
                # for l in range(X.shape[0]):
                #     temp = np.transpose(X[l, :, :])
                #     _X[l, :] = temp.flatten()
                # X = _X

        if not whole_history:
            if convolution == 1:
                print('only whole time history with lstm')
                # print('adding one virtual time stamp')
                # X = X[..., np.newaxis, :]
                return

        print('number of nan/infinity features')
        print(np.isnan(X).sum(axis=0).sum())
        print(np.isinf(X).sum(axis=0).sum())
        print('number of nan/infinity output')
        print(np.isnan(y).sum(axis=0).sum())
        print(np.isinf(y).sum(axis=0).sum())

        print(np.count_nonzero(~np.isnan(X)))

        if self.maximum_precision:
            X = np.float64(X)
            y = np.float64(y)
        else :
            X = np.float32(X)
            y = np.float32(y)


        neural_net_precision = None
        if X.dtype == np.float64:
            neural_net_precision = torch.float64
        if X.dtype == np.float32:
            neural_net_precision = torch.float32

        activation_function = utility.convertActivationType(activation_type)

        if convolution == 1:
            # the number of figures
            input_size = X.shape[2]
            hidden_size = int(layers[-1]/2)
            num_layers = 1
            num_classes = y.shape[1]
            tm = roll_multi_layer_lstm.RollMultiLayerLSTM(
                X=X,
                y=y,
                num_classes=num_classes,
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                # nn.Softmax/nn.Softmin can be good activations for this problem
                x_type=neural_net_precision,
                y_type=neural_net_precision
                # activation_kwargs={'dim':1} # Parameter needed for nn.Softmax/nn.Softmin
            )
            tm.set_optimizer(nn.MSELoss, torch.optim.Adam, lr_type, lr=lr_start, betas=(0.9, 0.999), amsgrad=True)
            tm = tm.set_roll_period(n, s, repass_steps=epochs)
        elif convolution == 0:
            tm = roll_multi_layer_perceptron.RollMultiLayerPerceptron(
                X=X,
                y=y,
                layers=layers,
                activation=activation_function,  # nn.Softmax/nn.Softmin can be good activations for this problem
                x_type=neural_net_precision,
                y_type=neural_net_precision,
                # activation_kwargs={'dim':1} # Parameter needed for nn.Softmax/nn.Softmin
            )
            tm.set_optimizer(nn.MSELoss, torch.optim.Adam, lr_type, lr=lr_start, betas=(0.9, 0.999), amsgrad=True)
            tm = tm.set_roll_period(n, s, repass_steps=epochs)
        elif convolution == 2:
            tm = roll_lightgbm.RollLightGbm(
                X=X,
                y=y
            )
            tm = tm.set_roll_period(n, s)

        features_df, predictions_df, returns_df = tm.unroll_features(dates, features_names)
        return features_df, predictions_df, returns_df

    def ratio_computer(self,features_df=None, features_segmentation = {}, tol = 1e-6):
        features_names = list(features_df.columns)
        extended_features_segmentation = {}
        for key, values in features_segmentation.items():
            selected_columns = []
            for feature_value in values:
                selected_columns.extend([col for col in features_names if feature_value in col])
                extended_features_segmentation[key] = selected_columns

        # aggregating features importance
        features_importance = features_df.sum(axis=0)
        features_importance = pd.DataFrame(
            {'col': features_importance.index, 'features_importance': features_importance.values})
        features_importance.sort_values('features_importance', inplace=True, ascending=False)

        all_group_features_importance = None
        for key, features_group in extended_features_segmentation.items():
            print('Features group ' + key)
            print('Number of  features for this group ' + str(len(features_group)))
            features_bool_indexing = [True if col in features_group else False for col in features_importance.col]
            group_features_importance = features_importance[features_bool_indexing]
            print('merging in a common dataframe')
            group_features_importance['group'] = key
            if all_group_features_importance is None:
                all_group_features_importance = group_features_importance
            else:
                all_group_features_importance = all_group_features_importance.append(group_features_importance,
                                                                                     ignore_index=True)

        features_importance_summarized = all_group_features_importance.groupby('group')['features_importance'].sum()
        features_importance_summarized = features_importance_summarized / features_importance_summarized.sum()
        if 'Dates' in features_df:
            dates = features_df.Dates
        else:
            dates = pd.to_datetime(features_df.index)

        part_over_time_df = None

        for key, features_values in extended_features_segmentation.items():
            grouped_features_df = features_df[features_values]
            if part_over_time_df is None:
                temp = (grouped_features_df.abs()+tol).sum(axis=1)
                temp.columns = [key]
                part_over_time_df = temp
            else:
                temp = (grouped_features_df.abs()+tol).sum(axis=1)
                temp.columns = [key]
                new_columns = list(part_over_time_df.columns)+[key]
                part_over_time_df = pd.concat([part_over_time_df, temp],axis=1)
                part_over_time_df.columns = new_columns



        part_over_time_df = part_over_time_df.div(part_over_time_df.sum(axis=1), axis=0)

        part_over_time_df.index = dates
        return features_importance_summarized, part_over_time_df








