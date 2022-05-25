import gc
import inspect as isp
from typing import Optional, Callable, Union, List, Tuple

import numpy as np
import torch as T
from scipy.special import softmax, expit as sigmoid
from sklearn.base import ClassifierMixin, RegressorMixin, BaseEstimator
from sklearn.model_selection import StratifiedShuffleSplit, ShuffleSplit
from sklearn.utils.validation import check_is_fitted
from torch import nn

from .learner import Learner
from ..callbacks import BaseCallback, CallbackList


def get_module_params(module_cls, kwargs):
    init_signature = isp.signature(module_cls.__init__)
    params = {p.name: kwargs[p.name] for p in init_signature.parameters.values() if p.name != 'self' and p.kind != p.VAR_POSITIONAL and p.name in kwargs}
    return params


class _SKWrapperBase(BaseEstimator):
    def get_params(self, deep=True):
        # todo: don't support `deep` for kwargs.
        # todo: check attributes
        out = super().get_params(deep)
        out.update(self._kwargs)
        return out

    def set_params(self, **params):
        _ = super().set_params(**params)
        for k, v in params.items():
            if k in self._kwargs:
                self._kwargs[k] = v
        return self

    def _init_learner(self):
        self.learner_ = getattr(self, 'learner_', None) if self.warm_start else None
        if self.learner_ is None:
            module = self.module_cls(**get_module_params(self.module_cls, self._kwargs))
            self.learner_: Learner = self.learner_cls(module, self.optimizer_fn, self.loss_fn, self.swa, self.avg_fn, self.amp)

    def __init__(self, module_cls: Optional[type] = None, optimizer_fn: Optional[Union[Callable, T.optim.Optimizer]] = None,
                 loss_fn: Optional[Union[Callable, nn.Module]] = None, warm_start: bool = False,
                 swa=False, avg_fn=None, amp=False,
                 epochs: int = 10, batch_size: Optional[int] = 128, metrics: Optional[List[Tuple[int, str, Callable]]] = None,
                 validation_fraction: float = 0.1, random_state: Optional[float] = None,
                 callbacks: Optional[Union[List[BaseCallback], CallbackList]] = None,
                 device: Union[str, T.device] = 'cpu', learner_cls: type = Learner, verbose: bool = True,
                 **kwargs):
        # kwargs: 传给模型的/Learner.fit
        self.module_cls = module_cls
        self.optimizer_fn = optimizer_fn
        self.loss_fn = loss_fn
        self.warm_start = warm_start
        self.swa = swa
        self.avg_fn = avg_fn
        self.amp = amp
        self.epochs = epochs
        self.batch_size = batch_size
        self.metrics = metrics
        self.validation_fraction = validation_fraction
        self.random_state = random_state
        self.callbacks = callbacks
        self.device = device
        self.learner_cls = learner_cls
        self.verbose = verbose
        self._kwargs = kwargs
        vars(self).update(kwargs)

    def __del__(self):
        # todo: clear self
        if hasattr(self, 'learner_'):
            del self.learner_
        T.cuda.empty_cache()
        gc.collect()


class NNClassifier(ClassifierMixin, _SKWrapperBase):
    def fit(self, X: np.ndarray, y: np.ndarray):
        self._init_learner()
        cv = StratifiedShuffleSplit(test_size=self.validation_fraction, random_state=self.random_state)
        idx_train, idx_val = next(cv.split(X, y))
        train_ds = (X[idx_train], y[idx_train])
        val_ds = (X[idx_val], y[idx_val])
        self.learner_.fit(train_ds, self.epochs, self.batch_size, self.metrics, validation_set=val_ds, callbacks=self.callbacks, device=self.device,
                          verbose=self.verbose, **self._kwargs)
        return self

    def predict_proba(self, X: np.ndarray, **kwargs):
        check_is_fitted(self)
        logit = self.learner_.predict(X, self.batch_size, self.device, **kwargs)
        if logit.shape[1] == 1:
            return sigmoid(logit)
        return softmax(logit)

    def predict(self, X: np.ndarray, **kwargs):
        check_is_fitted(self)
        prob = self.predict_proba(X, **kwargs)
        if prob.shape[1] == 1:
            return (prob > 0.5).astype(int)
        return prob.argmax(1)


class NNRegressor(RegressorMixin, _SKWrapperBase):
    def fit(self, X: np.ndarray, y: np.ndarray):
        self._init_learner()
        cv = ShuffleSplit(test_size=self.validation_fraction, random_state=self.random_state)
        idx_train, idx_val = next(cv.split(X, y))
        train_ds = (X[idx_train], y[idx_train])
        val_ds = (X[idx_val], y[idx_val])
        self.learner_.fit(train_ds, self.epochs, self.batch_size, self.metrics, validation_set=val_ds, callbacks=self.callbacks, device=self.device,
                          verbose=self.verbose, **self._kwargs)
        return self

    def predict(self, X: np.ndarray, **kwargs):
        check_is_fitted(self)
        return self.learner_.predict(X, **kwargs)
