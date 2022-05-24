#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from sklearn.metrics import mean_squared_error
from cryptotoolbox.roller import roller
import pickle
import shap
import pandas as pd
import torch.nn
import torch
import torch.nn as nn
from torch.autograd import Variable

from cryptotoolbox.callback import ts_callback
from functools import partial

class _ShortCutLSTMBaseNeuralNet(torch.nn.Module):
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
    def train_on(self, X, X_shortcut, y):
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
        # if self.num_layers>1:
        #     duplicate_y = torch.cat((y, y), 0)
        # else:
        #     duplicate_y = y
        # loss = self.criterion(outputs, duplicate_y)
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
            self=self.double()

        if hasattr(self, 'N') and self.N != X.size(1):
            raise ValueError('X must have {} input columns'.foramt(self.N))

        if hasattr(self, 'M') and self.M != y.size(1):
            raise ValueError('y must have {} output columns'.format(self.M))

        self.X = self._set_data(X)
        self.X_shortcut = self._set_data(X_shortcut)
        self.y = self._set_data(y)

        if self.X.ndim == 2:
            self.T, self.N = self.X.size()
            T_veri, self.M = self.y.size()
        if self.X.ndim == 3:
            self.T,self.H, self.N = self.X.size()
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


class MultiLayerShortCutLSTM(_ShortCutLSTMBaseNeuralNet):
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

    def __init__(self, X, X_shortcut, y, num_classes, input_size, hidden_size, num_layers,x_type=None, y_type=None, activation = None):
        """ Initialize object. """
        _ShortCutLSTMBaseNeuralNet.__init__(self)
        super(MultiLayerShortCutLSTM, self).__init__()

        self.set_data(X=X, X_shortcut=X_shortcut ,y=y, x_type=x_type, y_type=y_type)

        self.num_classes = num_classes
        self.num_layers = num_layers
        self.input_size = input_size
        self.shortcut_size = X_shortcut.shape[1]
        self.hidden_size = hidden_size

        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)

        self.fc = nn.Linear(hidden_size+self.shortcut_size, num_classes)
        # Set activation functions
        if activation is None:
            self.activation = lambda x: x
        else:
            self.activation = activation



    def forward(self, x, x_shortcut):
        # # reset the state of LSTM
        # # the state is kept till the end of the past sequence for the batch
        # h_batch = Variable(torch.zeros(
        #     self.num_layers, x.size(0), self.hidden_size))
        # c_batch = Variable(torch.zeros(
        #     self.num_layers, x.size(0), self.hidden_size))
        # # Propagate input through LSTM
        # ula, (h_out, _) = self.lstm(x, (h_batch, c_batch))

        ula, (h_out, _) = self.lstm(x)
        #clip = 0.001
        #torch.nn.utils.clip_grad_norm(self.lstm.parameters(), clip)

        h_out = h_out.view(-1, self.hidden_size)
        #print(h_out.shape)

        out = torch.cat([h_out, x_shortcut], dim=1)
        out = self.fc(out)

        #print(out.shape)
        out = self.activation(out)
        if self.num_layers>1:
            out = out[-x.shape[0]:]
        return out

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

class RollMultiLayerShortCutLSTM(MultiLayerShortCutLSTM, roller._ShortCutRollingBasis):
    """ Rolling version of the vanilla neural network model.
    TODO:
    - fix train and predict methods
    - finish docstring
    - finish methods
    """

    def __init__(self, X, X_shortcut, y, num_classes, input_size, hidden_size, num_layers, x_type = None, y_type = None, activation=None):
        """ Initialize rolling multi-layer perceptron model. """
        roller._ShortCutRollingBasis.__init__(self, X, X_shortcut, y)
        MultiLayerShortCutLSTM.__init__(self, X, X_shortcut, y, num_classes=num_classes, input_size=input_size,
                                hidden_size=hidden_size, num_layers=num_layers,x_type = x_type, y_type = y_type, activation = activation)
        assert x_type == y_type
        if x_type == torch.float64:
            self.double()

    def set_roll_period(self, train_period, test_period, start=0, end=None, repass_steps=1):
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

    def _train(self, X,X_shortcut,y):
        return self.train_on(X=X, X_shortcut=X_shortcut, y=y)

    def sub_predict(self, X, X_shortcut):
        """ Predict. """
        return self.predict(X=X,X_shortcut=X_shortcut)

    def eval_predictor_importance(self, features, features_names):
        explainer_shap = shap.GradientExplainer(model=self,
                                            data=features)
        # Fit the explainer on a subset of the data (you can try all but then gets slower)
        shap_values = explainer_shap.shap_values(X=features,
                                                 ranked_outputs=True)

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

    def unroll(self, display_slices=False):
        self.handle_callback('begin_fit')
        for eval_slice, test_slice in self:
            # Compute prediction on eval and test set
            self.y_eval[eval_slice] = self.sub_predict(self.X[eval_slice],self.X_shortcut[eval_slice])
            predictors = self.X[test_slice]
            test_prediction = self.sub_predict(self.X[test_slice],self.X_shortcut[test_slice])
            if abs(test_prediction.numpy().sum())<= 1e-6:
                print('null prediction, investigate')
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
            if np.random.rand()>=0.8:
                print(txt)
            if display_slices:
                print('eval slice '+str(eval_slice))
                print('test slice ' + str(test_slice))
                print(self.X[test_slice])
                print(tt.sum())
                print(tt_true.sum())

        self.last_eval_slice = eval_slice
        self.last_test_slice = test_slice
        return eval_slice, test_slice, predictors,  tt ,  tt_true

    def print_parameters(self):
        # Print model's state_dict
        print("to be done")

    def save_model_and_last_state(self, state=None, model_path=''):
        file_obj = open(model_path+'_py.obj', 'wb')
        pickle.dump(state, file_obj)
        file_obj.close()

    def resume_state(self, model_path=''):
        file_obj = open(model_path+'_py.obj', 'rb')
        self.state = pickle.load(file_obj)
        return self.state