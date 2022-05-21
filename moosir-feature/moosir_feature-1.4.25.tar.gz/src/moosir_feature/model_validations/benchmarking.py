import pandas as pd
import numpy as np

from sklearn.base import RegressorMixin
from sklearn.model_selection import cross_validate

from .metrics import get_any_metric

class NaiveModel(RegressorMixin):
    """
     - lag target of look_back_len retuns as prediction
    """

    def __init__(self, targets: pd.DataFrame, look_back_len: int):
        # self.rand_seed = rand_seed if rand_seed is not None else np.random.randint(0, 1000)
        self.look_back_len = look_back_len
        self.targets = targets

    def fit(self, X=None, y=None):
        pass

    def predict(self, X):
        vals = self.targets[self.targets.index.isin(X.index)]

        iloc_last = self.targets.index.get_loc(X.index.min())
        val_last = self.targets.iloc[iloc_last - self.look_back_len]
        vals = vals.shift(self.look_back_len).dropna()
        result = np.append(val_last, vals.values.reshape(-1))

        return result

    def get_params(self, deep=False):
        return {'look_back_len': self.look_back_len, 'targets': self.targets}

    def set_params(self, **parameters):
        self.look_back_len = parameters['look_back_len']
        self.targets = parameters['targets']
        return self


class RandomModel(RegressorMixin):
    def __init__(self, min, max):
        # self.rand_seed = rand_seed if rand_seed is not None else np.random.randint(0, 1000)
        self.min = min
        self.max = max

    def fit(self, X=None, y=None):
        pass

    def predict(self, X):
        vals = np.random.uniform(self.min, self.max, (len(X), 1))
        return vals

    def get_params(self, deep=False):
        return {'min': self.min, 'max': self.max}

    def set_params(self, **parameters):
        self.min = parameters['min']
        self.max = parameters['max']
        return self

def run_benchmarking(models: list, cv, features: pd.DataFrame, targets: pd.DataFrame, metrics: list):
    """

    :param models: list of models to be selected from
    :param cv: cv to run the models
    :param features: features
    :param targets: targets
    :return: benchmarking result
      fit_time	score_time test_<metric1> ... test_<metricn>, Model, Split_Cv
      --------	---------- -------------- ... --------------  -----  --------

    """
    cv_results = []
    scorers = get_any_metric(metrics=metrics)
    for model in models:

        cv_result = pd.DataFrame(cross_validate(estimator=model, cv=cv, X=features, y=targets,
                                                scoring=scorers))
        cv_result['Model'] = type(model).__name__
        cv_result['Split_Cv'] = pd.Series(data=cv_result.index.values, index=cv_result.index)

        cv_results.append(cv_result)

    result = pd.concat(cv_results, axis=0).reset_index()
    _ = result.pop("index")
    return result
