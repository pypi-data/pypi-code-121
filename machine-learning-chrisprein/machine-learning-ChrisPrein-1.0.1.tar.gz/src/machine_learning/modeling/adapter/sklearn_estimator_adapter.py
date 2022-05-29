from ...evaluation.abstractions.evaluation_metric import TModel
from ..abstractions.model import Model, TInput, TTarget
from sklearn.base import BaseEstimator
from typing import Dict, Any, TypeVar, Generic
import copy

class SkleanEstimatorAdapter(Generic[TModel], BaseEstimator):
    def __init__(self, prototype_model: TModel=None, **sk_params):
        self.sk_params = sk_params
        self.prototype_model: TModel = prototype_model
        self.model: TModel = self.prototype_model.__class__(self.sk_params)
        # self.model: TModel = copy.deepcopy(self.prototype_model)

    def fit(self, X, y, **kwargs):

        for input, target in zip(X, y):
            self.model.train(input, target)
        
        return self

    def predict(self, X):
        return [self.model.predict(input) for input in X]

    def get_params(self, **params):
        res = copy.deepcopy(self.sk_params)
        res.update({'prototype_model': self.prototype_model})
        return res

    def set_params(self, **params):
        self.sk_params.update(params)
        return self