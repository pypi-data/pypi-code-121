#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod

import pandas as pd

import numpy as np

from cryptotoolbox.neural_net import roll_multi_layer_lstm
from cryptotoolbox.neural_net import roll_multi_layer_shortcut_lstm


from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.neural_net import roll_multi_layer_perceptron
from cryptotoolbox.neural_net import roll_multi_layer_shortcut_perceptron
from cryptotoolbox.boosted_trees import roll_lightgbm
from cryptotoolbox.features import features_type
from cryptotoolbox.utility import weights
from cryptotoolbox.model_state import resuming_state
from cryptotoolbox.utility import utility

import torch
import torch.nn as nn



class AbstractRunner(ABC):
    def __init__(self, starting_date = None, running_date = None, drop_token=None, dropbox_backup = True, save_model=False, supervision_npy_file_suffix='_supervision.npy', macro_supervision_npy_file_suffix='_macro_supervision.npy', features_saving_suffix='_features.npy', features_names_saving_suffix='_features_names.npy', shortcut_features_names_saving_suffix = '_shortcut_features_names.npy', shortcut_features_saving_suffix='_shortcut_features.npy',returns_pkl_file_suffix='_returns.pkl',  local_root_directory='../data/', user = 'napoleon', n_start = 252, maximum_precision = False, shortcut_features = False, transaction_costs = None, crypto_ticker = None):
        super().__init__()
        self.local_root_directory=local_root_directory
        self.supervision_npy_file_suffix=supervision_npy_file_suffix
        self.macro_supervision_npy_file_suffix=macro_supervision_npy_file_suffix
        self.features_saving_suffix=features_saving_suffix
        self.features_names_saving_suffix=features_names_saving_suffix

        self.returns_pkl_file_suffix=returns_pkl_file_suffix

        self.shortcut_features_saving_suffix = shortcut_features_saving_suffix
        self.shortcut_features_names_saving_suffix = shortcut_features_names_saving_suffix
        self.shortcut_features = shortcut_features
        self.user=user
        self.n_start = n_start
        self.dropbox_backup = dropbox_backup
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.save_model = save_model
        self.running_date = running_date
        self.starting_date = starting_date
        self.maximum_precision = maximum_precision
        self.transaction_costs = transaction_costs


        self.crypto_ticker = crypto_ticker
        if self.crypto_ticker is not None:
            self.returns_pkl_file_name =  self.crypto_ticker + '_' +self.starting_date.strftime('%d_%b_%Y') + '_' + self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix
        else :
            self.returns_pkl_file_name = self.running_date.strftime('%d_%b_%Y') + self.returns_pkl_file_suffix



    @abstractmethod
    def runTrial(self,saver, seed, sup, layers, epochs, n_past_features, n, s, whole_history, advance_feature, advance_signal,
                 normalize, activation_string, convolution, lr_start, lr_type, low_bound, up_bound):
        pass


class SimpleRunner(AbstractRunner):
    def runTrial(self, saver, seed, sup, layers, epochs, n_past_features, n, s, feature_type, activation_type, convolution, lr_start, lr_type, low_bound, up_bound, normalize):
        if (feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED) and n_past_features is None:
            print('n_past_features must not be None for LSTM history features')
            return
        if (feature_type is features_type.FeaturesType.STANDARD or feature_type is features_type.FeaturesType.STANDARD_ADVANCED) and n_past_features is not None:
            print('n_past_features must be None for LSTM history features')
            return

        saving_key = saver.create_saving_key(seed, sup, layers, epochs, n_past_features, n, s, feature_type, activation_type, convolution, lr_start, lr_type, low_bound, up_bound, normalize)
        print('Launching computation with parameters : '+saving_key)


        ## checking if the computation has already been done
        run_found, found_table_number = saver.checkRunExistence(saving_key)
        if run_found:
            print('Run already present in table '+str(found_table_number)+' : we do nothing')
            return

        supervisors = {}
        supervisors['f_minVar'] = 0
        supervisors['f_maxMean'] = 1
        supervisors['f_sharpe'] = 2
        supervisors['f_MeanVar'] = 3
        supervisors['f_calmar'] = 4
        supervisors['f_drawdown'] = 5

        print('running date '+str(self.running_date))

        df = self.dbx.local_overwrite_and_load_pickle( folder='', subfolder='', returns_pkl_file_name=self.returns_pkl_file_name, local_root_directory = self.local_root_directory)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df[df.index>=self.starting_date]
        df = df[df.index<=self.running_date]
        df = df.fillna(method='ffill')
        print('returns size  '+str(df.shape))
        print('min running date '+str(min(df.index)))
        print('max running date '+str(max(df.index)))

        print('loading supervision results')
        result =self.dbx.local_supervision_npy_overwrite_and_load_array(starting_date= self.starting_date, ending_date = self.running_date, rebal = s , lower_bound= low_bound, upper_bound = up_bound, local_root_directory= self.local_root_directory, user = self.user, supervision_npy_file_suffix= self.supervision_npy_file_suffix)
        print('supervision results shape')
        print(result.shape)

        np.random.seed(seed)
        torch.manual_seed(seed)
        # Set data
        whole_history = (feature_type is features_type.FeaturesType.HISTORY or feature_type is features_type.FeaturesType.HISTORY_ADVANCED)

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
        X_shortcut = shortcut_features[self.n_start:]

        y = result[self.n_start:, :, supervisors[sup]]
        df = df.iloc[self.n_start:]

        print('predictors')
        print(X.shape)
        print('utility')
        print(y.shape)
        print('prices')
        print(df.shape)

        assert df.shape[0] >= X.shape[0]
        assert df.shape[0] >= y.shape[0]

        # convolution 0 : perceptron
        # convolution 1 : LSTM
        # convolution 2 : xgboost
        if whole_history:
            if convolution == 2:
                print('no whole time history with ensembling method')
                return
            if convolution == 0:
                print('no whole time history with multi layers perceptron')
                return
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
            X_shortcut = np.float64(X_shortcut)
            y = np.float64(y)
        else :
            X = np.float32(X)
            X_shortcut = np.float32(X_shortcut)
            y = np.float32(y)


        neural_net_precision = None
        if X.dtype == np.float64:
            neural_net_precision = torch.float64
        if X.dtype == np.float32:
            neural_net_precision = torch.float32

        activation_function = utility.convertActivationType(activation_type)

        if self.shortcut_features:
            if convolution == 1:
                # the number of figures
                input_size = X.shape[2]
                hidden_size = int(layers[-1])
                num_layers = int(layers[-2])
                num_classes = y.shape[1]
                tm = roll_multi_layer_shortcut_lstm.RollMultiLayerShortCutLSTM(
                    X=X,
                    X_shortcut=X_shortcut,
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
                tm = roll_multi_layer_shortcut_perceptron.RollMultiLayerShortCutPerceptron(
                    X=X,
                    X_shortcut=X_shortcut,
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
        else :
            if convolution == 1:
                # the number of figures
                input_size = X.shape[2]
                hidden_size = int(layers[-1])
                num_layers = int(layers[-2])
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

        eval_slice, test_slice, predictors, tt, tt_true = tm.unroll()

        dates_eval_slice, dates_test_slice = df.index[eval_slice], df.index[test_slice]

        state = resuming_state.ModelState(
            eval_slice = eval_slice,
            test_slice = test_slice,
            dates_eval_slice = dates_eval_slice,
            dates_test_slice = dates_test_slice,
            df_eval = df.loc[dates_eval_slice],
            df_test = df.loc[dates_test_slice],
            X_eval = X[eval_slice],
            X_test = X[test_slice],
            y_eval = y[eval_slice],
            y_test = y[test_slice],
            pred_test = tm.y_test[test_slice],
            pred_eval = tm.y_eval[eval_slice]
        )

        recordings_df, activations_df = tm.recorder.get_all_recordings()
        print('recordings '+str(list(recordings_df.columns)))
        print('activations ' + str(list(activations_df.columns)))

        # tm.y_test[tm.t:] = tm.sub_predict(tm.X[tm.t:])
        df_ret = df.fillna(method='bfill').pct_change().fillna(0).copy()

        ### getting the transaction costs
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

            costs_parameters = np.fromiter(map(lambda x: get_fees_rate(x, self.transaction_costs), df_ret.columns),
                                           dtype=np.float64)
        # Process weights
        print('processing weights for '+saving_key)
        weight_mat, last_predicted_weights = weights.process_weights(w=tm.y_test, df=df_ret, s=s, n=n, low_bound=low_bound, up_bound=up_bound,normalize=normalize)
        # Compute portfolio perf
        transaction_costs_matrix = abs(weight_mat - weight_mat.shift(1)) *costs_parameters
        adjusted_returns = df_ret * weight_mat.values - transaction_costs_matrix
        portfolio = np.cumprod(np.prod(adjusted_returns + 1, axis=1))
        if self.save_model :
            tm.save_model_and_last_state(state=state,model_path = self.local_root_directory+saving_key)
        if self.dropbox_backup:
            self.dbx.uploadFileToDropbox(filename=saving_key+'_model.torch', dropbox_subfolder = '', fullpath=self.local_root_directory+saving_key+'_model.torch')
            self.dbx.uploadFileToDropbox(filename=saving_key+'_py.obj', dropbox_subfolder = '', fullpath=self.local_root_directory+saving_key+'_py.obj')

        saver.saveResults(saving_key, portfolio, weight_mat, recordings_df, activations_df, last_predicted_weights)
        print('saved '+ saving_key)
        return  last_predicted_weights


