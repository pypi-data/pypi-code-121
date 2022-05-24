
#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from cryptotoolbox.callback import ts_callback

from functools import partial
import torch.nn as nn
import numpy as np

class _RollingBasis:
    """ Base object to roll a neural network model.
    Rolling over a time axis with a train period from `t - n` to `t` and a
    testing period from `t` to `t + s`.
    Parameters
    ----------
    X, y : array_like
        Respectively input and output data.
    f : callable, optional
        Function to transform target, e.g. ``torch.sign`` function.
    index : array_like, optional
        Time index of data.
    Methods
    -------
    __call__
    Attributes
    ----------
    n, s, r : int
        Respectively size of training, testing and rolling period.
    b, e, T : int
        Respectively batch size, number of repass_steps and size of entire dataset.
    t : int
        The current time period.
    y_eval, y_test : np.ndarray[ndim=1 or 2, dtype=np.float64]
        Respectively evaluating (or training) and testing predictions.
    """

    def __init__(self, X, y, cbs=None, cb_funcs=None):
        """ Initialize shape of target. """
        self.T = X.shape[0]
        self.y_shape = y.shape
        self.idx = np.arange(self.T)

        if cb_funcs is None:
            cb_funcs = [ts_callback.Recorder,
                        ts_callback.TrainEvalCallback]

        cbs = ts_callback.listify(cbs)
        for cbf in ts_callback.listify(cb_funcs):
            cb = cbf()
            setattr(self, cb.name, cb)
            cbs.append(cb)
        self.cbs = cbs
        for cb in self.cbs: cb.set_runner(self)


    def handle_callback(self, cb_name, **kwargs):
        for cb in sorted(self.cbs, key=lambda x: x._order):
            f = getattr(cb, cb_name, None)
            if f and f(**kwargs): return True
        return False

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
        repass_stepss : int, optional
            Number of repass_stepss on the same subperiod, default is 1.
        Returns
        -------
        _RollingBasis
            The rolling basis model.
        """
        # Set size of subperiods
        self.n = train_period
        self.s = test_period
        self.repass_steps = repass_steps

        # Set boundary of period
        self.T = self.T if end is None else min(self.T, end)
        self.t = max(self.n - self.s, start)

        return self

    def __iter__(self):
        """ Set iterative method. """
        self.y_eval = np.zeros(self.y_shape)
        self.y_test = np.zeros(self.y_shape)
        self.loss_train = []
        self.loss_eval = []
        self.loss_test = []

        return self

    def __next__(self):
        self.t += self.s

        if self.t > (self.T-1):
            raise StopIteration

        if self.t + self.s > self.T:
            # output to train would need the future : we do not retrain the networl
            return slice(self.t - self.s, self.t), slice(self.t, self.T)

        self.handle_callback('begin_batch')
        for repass_step in range(self.repass_steps):
            self.handle_callback('begin_repass')
            train_slice = slice(self.t - self.n, self.t-self.s)
            lo = self._train(
                X=self.X[train_slice],
                y=self.y[train_slice],
            )
            self.handle_callback('after_repass')
            self.loss_train += [lo]
        self.handle_callback('after_batch')
        # Set eval and test periods
        return slice(self.t - self.s, self.t-1), slice(self.t, self.t + self.s-1)




class _ShortCutRollingBasis:
    """ Base object to roll a neural network model.
    Rolling over a time axis with a train period from `t - n` to `t` and a
    testing period from `t` to `t + s`.
    Parameters
    ----------
    X, y : array_like
        Respectively input and output data.
    f : callable, optional
        Function to transform target, e.g. ``torch.sign`` function.
    index : array_like, optional
        Time index of data.
    Methods
    -------
    __call__
    Attributes
    ----------
    n, s, r : int
        Respectively size of training, testing and rolling period.
    b, e, T : int
        Respectively batch size, number of repass_steps and size of entire dataset.
    t : int
        The current time period.
    y_eval, y_test : np.ndarray[ndim=1 or 2, dtype=np.float64]
        Respectively evaluating (or training) and testing predictions.
    """

    def __init__(self, X,X_shortcut, y, cbs=None, cb_funcs=None):
        """ Initialize shape of target. """
        self.T = X.shape[0]
        self.y_shape = y.shape
        self.idx = np.arange(self.T)

        if cb_funcs is None:
            cb_funcs = [ts_callback.Recorder,
                        ts_callback.TrainEvalCallback]

        cbs = ts_callback.listify(cbs)
        for cbf in ts_callback.listify(cb_funcs):
            cb = cbf()
            setattr(self, cb.name, cb)
            cbs.append(cb)
        self.cbs = cbs
        for cb in self.cbs: cb.set_runner(self)


    def handle_callback(self, cb_name, **kwargs):
        for cb in sorted(self.cbs, key=lambda x: x._order):
            f = getattr(cb, cb_name, None)
            if f and f(**kwargs): return True
        return False

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
        repass_stepss : int, optional
            Number of repass_stepss on the same subperiod, default is 1.
        Returns
        -------
        _RollingBasis
            The rolling basis model.
        """
        # Set size of subperiods
        self.n = train_period
        self.s = test_period
        self.repass_steps = repass_steps

        # Set boundary of period
        self.T = self.T if end is None else min(self.T, end)
        self.t = max(self.n - self.s, start)

        return self

    def __iter__(self):
        """ Set iterative method. """
        self.y_eval = np.zeros(self.y_shape)
        self.y_test = np.zeros(self.y_shape)
        self.loss_train = []
        self.loss_eval = []
        self.loss_test = []

        return self

    def __next__(self):
        self.t += self.s

        if self.t > self.T:
            raise StopIteration

        if self.t + self.s > self.T:
            # output to train would need the future : we do not retrain the networl
            return slice(self.t - self.s, self.t), slice(self.t, self.T)

        self.handle_callback('begin_batch')
        for repass_step in range(self.repass_steps):
            self.handle_callback('begin_repass')
            train_slice = slice(self.t - self.n, self.t-self.s)
            lo = self._train(
                X=self.X[train_slice],
                X_shortcut = self.X_shortcut[train_slice],
                y=self.y[train_slice],
            )
            self.handle_callback('after_repass')
            self.loss_train += [lo]
        self.handle_callback('after_batch')
        # Set eval and test periods
        return slice(self.t - self.s, self.t-1), slice(self.t, self.t + self.s-1)

