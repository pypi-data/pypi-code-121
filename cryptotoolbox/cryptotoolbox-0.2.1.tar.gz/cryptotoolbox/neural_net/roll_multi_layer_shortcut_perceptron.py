#!/usr/bin/env python3
# coding: utf-8


import pandas as pd
import torch
import torch.nn
import numpy as np
import shap
import pickle

from sklearn.metrics import mean_squared_error

from cryptotoolbox.roller import roller
from cryptotoolbox.callback import ts_callback
from functools import partial
from functools import reduce

def list_average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)

class _ShortCutPerceptronBaseNeuralNet(torch.nn.Module):
    """ Base object for neural network model with PyTorch.
    Inherits of torch.nn.Module object with some higher level methods.
    Attributes
    ----------
    criterion : torch.nn.modules.loss
        A loss function.
    optimizer : torch.optim
        An optimizer algorithm.
    N, M : int
        Respectively input and output dimension.
    Methods
    -------
    set_optimizer
    train_on
    predict
    set_data
    See Also
    --------
    MultiLayerPerceptron, RollingBasis
    """

    def __init__(self):
        """ Initialize. """
        torch.nn.Module.__init__(self)

    def set_optimizer(self, criterion, optimizer, lr_type, **kwargs):
        """ Set the optimizer object.
        Set optimizer object with specified `criterion` as loss function and
        any `kwargs` as optional parameters.
        Parameters
        ----------
        criterion : torch.nn.modules.loss
            A loss function.
        optimizer : torch.optim
            An optimizer algorithm.
        **kwargs
            Keyword arguments of `optimizer`, cf PyTorch documentation [1]_.
        Returns
        -------
        BaseNeuralNet
            Self object model.
        References
        ----------
        .. [1] https://pytorch.org/docs/stable/optim.html
        """
        self.criterion = criterion()
        self.optimizer = optimizer(self.parameters(), **kwargs)
        self.lr = None
        lr = kwargs['lr']

        sched_standard = ts_callback.create_standard_annealing_profile(lr)
        cbf_func = partial(ts_callback.ParamScheduler, 'lr', sched_standard,lr_type)

        cb = cbf_func()
        setattr(self, cb.name, cb)
        cb.set_runner(self)
        self.cbs.append(cb)
        return self

    @torch.enable_grad()
    def train_on(self, X,X_shortcut,y):
        """ Trains the neural network model.
        Parameters
        ----------
        X, y : torch.Tensor
            Respectively inputs and outputs to train model.
        Returns
        -------
        torch.nn.modules.loss
            Loss outputs.
        """
        self.optimizer.zero_grad()
        outputs = self(X,X_shortcut)
        loss = self.criterion(outputs, y)
        loss.backward()
        self.optimizer.step()
        self.loss = loss.item()
        return loss.item()

    @torch.no_grad()
    def predict(self, X, X_shortcut):
        """ Predicts outputs of neural network model.
        Parameters
        ----------
        X : torch.Tensor
           Inputs to compute prediction.
        Returns
        -------
        torch.Tensor
           Outputs prediction.
        """
        return self(X,X_shortcut).detach()

    def set_data(self, X, X_shortcut, y, x_type=None, y_type=None):
        """ Set data inputs and outputs.
        Parameters
        ----------
        X, y : array-like
            Respectively input and output data.
        x_type, y_type : torch.dtype
            Respectively input and ouput data types. Default is `None`.
        """

        assert x_type == y_type

        if x_type == torch.float64:
            self = self.double()

        if hasattr(self, 'N') and self.N != X.size(1):
            raise ValueError('X must have {} input columns'.foramt(self.N))

        if hasattr(self, 'M') and self.M != y.size(1):
            raise ValueError('y must have {} output columns'.format(self.M))

        self.X = self._set_data(X)
        self.X_shortcut = self._set_data(X_shortcut)
        self.y = self._set_data(y)
        self.T, self.N = self.X.size()
        T_veri, self.M = self.y.size()

        if self.T != T_veri:
            raise ValueError('{} time periods in X differents of {} time \
                             periods in y'.format(self.T, T_veri))

        return self

    def _set_data(self, X):
        """ Convert array-like data to tensor. """
        # TODO : Verify dtype of data torch tensor
        if isinstance(X, np.ndarray):
            return torch.from_numpy(X)

        elif isinstance(X, pd.DataFrame):
            # TODO : Verify memory efficiancy
            return torch.from_numpy(X.values)

        elif isinstance(X, torch.Tensor):

            return X

        else:
            raise ValueError('Unkwnown data type: {}'.format(type(X)))


class MultiLayerShortCutPerceptron(_ShortCutPerceptronBaseNeuralNet):
    r""" Neural network with MultiLayer Perceptron architecture.
    Refered as vanilla neural network model, with `n` hidden layers s.t
    n :math:`\geq` 1, with each one a specified number of neurons.
    Parameters
    ----------
    X, y : array-like
        Respectively inputs and outputs data.
    layers : list of int
        List of number of neurons in each hidden layer.
    activation : torch.nn.Module
        Activation function of layers.
    drop : float, optional
        Probability of an element to be zeroed.
    Attributes
    ----------
    criterion : torch.nn.modules.loss
        A loss function.
    optimizer : torch.optim
        An optimizer algorithm.
    n : int
        Number of hidden layers.
    layers : list of int
        List with the number of neurons for each hidden layer.
    f : torch.nn.Module
        Activation function.
    Methods
    -------
    set_optimizer
    train_on
    predict
    set_data
    See Also
    --------
    BaseNeuralNet, RollMultiLayerPerceptron
    """

    def __init__(self, X, X_shortcut, y, layers=[], activation=None, drop=None,
                 x_type=None, y_type=None, bias=True, activation_kwargs={}):
        """ Initialize object. """
        _ShortCutPerceptronBaseNeuralNet.__init__(self)

        self.set_data(X=X,X_shortcut=X_shortcut, y=y, x_type=x_type, y_type=y_type)
        layers_list = []
        self.n_layers =  len(layers)
        # Set input layer
        input_size = self.N
        shortcut_size = X_shortcut.shape[1]
        for output_size in layers:
            # Set hidden layers
            layers_list += [torch.nn.Linear(
                input_size,
                output_size,
                bias=bias
            )]
            input_size = output_size

        # Set output layer
        self.final_layer = torch.nn.Linear(input_size+shortcut_size,self.M, bias=bias)
        #layers_list += [torch.nn.Linear(input_size, self.M, bias=bias)]
        self.layers = torch.nn.ModuleList(layers_list)
#        self.final_layer = torch.nn.Linear(layers[-1] )


        # Set activation functions
        # Set activation functions
        if activation is None:
            self.activation = lambda x: x
        else:
            self.activation = activation

        # Set dropout parameters
        if drop is not None:
            self.drop = torch.nn.Dropout(p=drop)

        else:
            self.drop = lambda x: x

    def forward(self, x, x_shortcut):
        """ Forward computation. """
        x = self.drop(x)
        self.handle_callback('after_layer', layer_index=0, layer_activ_mean=x.data.mean().item(),
                             layer_activ_std=x.data.std().item())
        for layer_index, layer in enumerate(self.layers):
            x = layer(x)
            x = self.activation(x)
            self.handle_callback('after_layer',layer_index = layer_index+1, layer_activ_mean=x.data.mean().item(), layer_activ_std = x.data.std().item())

        x = torch.cat([x, x_shortcut], dim=1)
        x = self.final_layer(x)
        x = self.activation(x)
        self.handle_callback('after_layer', layer_index=layer_index + 1, layer_activ_mean=x.data.mean().item(),
                             layer_activ_std=x.data.std().item())

        return x


def _type_convert(dtype):
    if dtype is np.float64 or dtype is np.float or dtype is np.double:
        return torch.float64

    elif dtype is np.float32:
        return torch.float32

    elif dtype is np.float16:
        return torch.float16

    elif dtype is np.uint8:
        return torch.uint8

    elif dtype is np.int8:
        return torch.int8

    elif dtype is np.int16 or dtype is np.short:
        return torch.int16

    elif dtype is np.int32:
        return torch.int32

    elif dtype is np.int64 or dtype is np.int or dtype is np.long:
        return torch.int64

    else:
        raise ValueError('Unkwnown type: {}'.format(str(dtype)))




class RollMultiLayerShortCutPerceptron(MultiLayerShortCutPerceptron, roller._ShortCutRollingBasis):
    """ Rolling version of the vanilla neural network model.
    TODO:
    - fix train and predict methods
    - finish docstring
    - finish methods
    """

    def __init__(self, X, X_shortcut, y, layers=[], activation=None, drop=None, bias=True,
                 x_type=None, y_type=None, activation_kwargs={}, **kwargs):
        """ Initialize rolling multi-layer perceptron model. """
        roller._ShortCutRollingBasis.__init__(self, X, X_shortcut, y, **kwargs)
        MultiLayerShortCutPerceptron.__init__(self, X, X_shortcut, y, layers=layers, bias=bias,
                                      activation=activation, drop=drop,
                                      x_type=x_type, y_type=y_type,
                                      activation_kwargs=activation_kwargs)
        if x_type == torch.float64:
            self.double()


    def set_roll_period(self, train_period, test_period, start=0, end=None,repass_steps=1):
        """ Callable method to set target features data, and model.
        Parameters
        ----------
        train_period, test_period : int
            Size of respectively training and testing sub-periods.
        start : int, optional
            Starting observation, default is first observation.
        end : int, optional
            Ending observation, default is last observation.
        roll_period : int, optional
            Size of the rolling period, default is the same size of the
            testing sub-period.
        eval_period : int, optional
            Size of the evaluating period, default is the same size of the
            testing sub-period if training sub-period is large enough.
        batch_size : int, optional
            Size of a training batch, default is 64.
        epochs : int, optional
            Number of epochs, default is 1.
        Returns
        -------
        _RollingBasis
            The rolling basis model.
        """
        return roller._ShortCutRollingBasis.set_roll_period(
            self, train_period=train_period, test_period=test_period,
            start=start, end=end, repass_steps=repass_steps
        )

    def _train(self, X, X_shortcut, y):
        return self.train_on(X=X,X_shortcut=X_shortcut, y=y)

    def sub_predict(self, X, X_shortcut):
        """ Predict. """
        return self.predict(X=X,X_shortcut = X_shortcut)

    def eval_predictor_importance(self, features, actual_predictions, features_names, check = True):
        deep_explainer = shap.DeepExplainer(self, features)
        shap_values = deep_explainer.shap_values(features)
        expected_values = deep_explainer.expected_value
        if check :
            for weight_index in range(actual_predictions.shape[1]):
                for prediction_index in range(actual_predictions.shape[0]):
                    weight_shap_values = shap_values[weight_index]
                    weight_expected_values = expected_values[weight_index]
                    weight_actual_predictions = actual_predictions.numpy()[:,weight_index]
                    weight_feature_effect = weight_shap_values.sum(axis=1)
                    weight_actual_predictions_from_shapley_values = weight_expected_values + weight_feature_effect
                    if np.sum(np.abs(weight_actual_predictions - weight_actual_predictions_from_shapley_values)) > 1e-6:
                        #raise Exception('Mismatch between shapley values and actual predictions')
                        print('Mismatch between shapley values and actual predictions')

        predictors_shap_values = [list_average(shap_values)]
        predictors_feature_order = np.argsort(np.sum(np.mean(np.abs(predictors_shap_values), axis=0), axis=0))

        predictors_left_pos = np.zeros(len(predictors_feature_order))

        predictors_class_inds = np.argsort([-np.abs(predictors_shap_values[i]).mean() for i in range(len(predictors_shap_values))])
        for i, ind in enumerate(predictors_class_inds):
            predictors_global_shap_values = np.abs(predictors_shap_values[ind]).mean(0)
            predictors_left_pos += predictors_global_shap_values[predictors_feature_order]

        predictors_ds = {}
        predictors_ds['features'] = np.asarray(features_names)[predictors_feature_order]
        predictors_ds['values'] = predictors_left_pos
        predictors_features_df = pd.DataFrame.from_dict(predictors_ds)
        values = {}
        for index, row in predictors_features_df.iterrows():
            values[row['features']]=row['values']

        return values

    def gradient_eval_predictor_importance(self, features, actual_predictions, features_names, display = False):
        explainer_shap = shap.GradientExplainer(model=self,
                                            data=features)
        # Fit the explainer on a subset of the data (you can try all but then gets slower)
        shap_values = explainer_shap.shap_values(features,nsamples = 500, ranked_outputs=True,output_rank_order='max',rseed=None,return_variances=False)
        predictors_shap_values = shap_values[0]
        predictors_feature_order = np.argsort(np.sum(np.mean(np.abs(predictors_shap_values), axis=0), axis=0))

        predictors_left_pos = np.zeros(len(predictors_feature_order))

        predictors_class_inds = np.argsort([-np.abs(predictors_shap_values[i]).mean() for i in range(len(predictors_shap_values))])
        for i, ind in enumerate(predictors_class_inds):
            predictors_global_shap_values = np.abs(predictors_shap_values[ind]).mean(0)
            predictors_left_pos += predictors_global_shap_values[predictors_feature_order]

        predictors_ds = {}
        predictors_ds['features'] = np.asarray(features_names)[predictors_feature_order]
        predictors_ds['values'] = predictors_left_pos
        predictors_features_df = pd.DataFrame.from_dict(predictors_ds)
        values = {}
        for index, row in predictors_features_df.iterrows():
            values[row['features']]=row['values']

        return values

    def unroll(self, display_slices = False):
        self.handle_callback('begin_fit')
        for eval_slice, test_slice in self:
            # Compute prediction on eval and test set
            eval_prediction = self.sub_predict(self.X[eval_slice], self.X_shortcut[eval_slice])
            self.y_eval[eval_slice] = eval_prediction
            predictors = self.X[test_slice]
            test_prediction = self.sub_predict(self.X[test_slice], self.X_shortcut[test_slice])
            self.y_test[test_slice] = test_prediction

            ev = self.y_eval[eval_slice]
            ev_true = self.y[eval_slice]

            tt = self.y_test[test_slice]
            tt_true = self.y[test_slice]

            self.loss_eval += [mean_squared_error(ev, ev_true)]
            self.loss_test += [mean_squared_error(tt, tt_true)]

            # Print loss on current eval and test set
            pct = (self.t - self.n - self.s) / (self.T - self.n - self.T % self.s)
            txt = '{:5.2%} is done | '.format(pct)
            txt += 'Eval loss is {:5.2} | '.format(self.loss_eval[-1])
            txt += 'Test loss is {:5.2} | '.format(self.loss_test[-1])
            if np.random.rand()>=0.9:
                print(txt)
            if display_slices:
                print('eval slice ' + str(eval_slice))
                print('test slice ' + str(test_slice))
                if self.X[eval_slice].shape == self.X[test_slice].shape:
                    m = (self.X[eval_slice] - self.X[test_slice])
                    distinct_frobenius = (m * m).sum().sqrt()
                    print('distinct frobenius between predictors ' + str(distinct_frobenius))
                    t = test_prediction - eval_prediction
                    distinct_frobenius_pred = (t * t).sum().sqrt()
                    print('distinct frobenius between predictions ' + str(distinct_frobenius_pred))
                if abs(test_prediction.numpy().sum()) <= 1e-6:
                    print('null prediction, investigate')

        self.last_eval_slice = eval_slice
        self.last_test_slice = test_slice
        return eval_slice, test_slice, predictors, tt, tt_true

    def unroll_features(self, dates, feature_names, display_slices = False, gradient = False):
        self.handle_callback('begin_fit')
        rows_list = []
        dates_list = []
        prediction_list = []
        truth_list = []
        for eval_slice, test_slice in self:
            # Compute prediction on eval and test set
            eval_prediction = self.sub_predict(self.X[eval_slice])
            self.y_eval[eval_slice] = eval_prediction
            test_prediction = self.sub_predict(self.X[test_slice])
            self.y_test[test_slice] = test_prediction
            ### features computation
            me_pred = torch.cat((eval_prediction, test_prediction), 0)
            me_features = torch.cat((self.X[eval_slice], self.X[test_slice]), 0)
            if gradient :
                features_dico = self.gradient_eval_predictor_importance(me_features, me_pred, feature_names)
            else:
                features_dico = self.eval_predictor_importance(me_features, me_pred, feature_names)
            rows_list.append(features_dico)
            dates_list.append(dates[test_slice.start])

            ### loss computation
            ev = self.y_eval[eval_slice]
            ev_true = self.y[eval_slice]

            tt = self.y_test[test_slice]
            tt_true = self.y[test_slice]

            prediction_list.append(self.y_test[test_slice.start])
            truth_list.append(self.y[test_slice.start])

            self.loss_eval += [mean_squared_error(ev, ev_true)]
            self.loss_test += [mean_squared_error(tt, tt_true)]

            # Print loss on current eval and test set
            pct = (self.t - self.n - self.s) / (self.T - self.n - self.T % self.s)
            txt = '{:5.2%} is done | '.format(pct)
            txt += 'Eval loss is {:5.2} | '.format(self.loss_eval[-1])
            txt += 'Test loss is {:5.2} | '.format(self.loss_test[-1])
            if np.random.rand()>=0.7:
                print(txt)
                if display_slices:
                    print('eval slice ' + str(eval_slice))
                    print('test slice ' + str(test_slice))
                    print('adding date '+ str(dates[test_slice.start]))
                    if self.X[eval_slice].shape == self.X[test_slice].shape:
                        m = (self.X[eval_slice] - self.X[test_slice])
                        distinct_frobenius = (m * m).sum().sqrt()
                        print('distinct frobenius between predictors ' + str(distinct_frobenius))
                        t = test_prediction - eval_prediction
                        distinct_frobenius_pred = (t * t).sum().sqrt()
                        print('distinct frobenius between predictions ' + str(distinct_frobenius_pred))
                    if abs(test_prediction.numpy().sum()) <= 1e-6:
                        print('null prediction, investigate')
        features_df = pd.DataFrame(rows_list)
        features_df.index = list(dates_list)
        predictions_df = pd.DataFrame(prediction_list)
        returns_df = pd.DataFrame(truth_list)
        predictions_df.index = list(dates_list)
        returns_df.index = list(dates_list)
        return features_df, predictions_df, returns_df

    def print_parameters(self):
        # Print model's state_dict
        print("Model's state_dict:")
        for param_tensor in self.state_dict():
            print(param_tensor, "\t", self.state_dict()[param_tensor].size())

        # Print optimizer's state_dict
        print("Optimizer's state_dict:")
        for var_name in self.optimizer.state_dict():
            print(var_name, "\t", self.optimizer.state_dict()[var_name])

    def save_model_and_last_state(self, state=None, model_path=''):

        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, model_path+'_model.torch')

        file_obj = open(model_path+'_py.obj', 'wb')
        pickle.dump(state, file_obj)
        file_obj.close()


    def resume_state(self, model_path=''):
        checkpoint = torch.load(model_path+'_model.torch')
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        file_obj = open(model_path+'_py.obj', 'rb')
        self.state = pickle.load(file_obj)
        return self.state




