import pandas as pd
import numpy as np
# from arch import arch_model
from sklearn.base import RegressorMixin
from sklearn.svm import SVR
import arch
from moosir_feature.transformers.features_common.calculator import align_features_and_targets, combine_features


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
        vals = vals.shift(self.look_back_len).fillna(val_last[0])
        # result = np.append(val_last, vals.values.reshape(-1))
        result = vals.values.reshape(-1)
        if len(X) != len (result):
            print("here ....")

        return result

    def get_params(self, deep=False):
        return {'look_back_len': self.look_back_len, 'targets': self.targets}

    def set_params(self, **parameters):
        self.look_back_len = parameters['look_back_len']
        self.targets = parameters['targets']
        return self




# todo: move to package
def select_windows(features: pd.DataFrame, targets: pd.DataFrame):
    # todo: really!!!
    features = features.dropna()
    features, targets, _ = align_features_and_targets(features=features,
                                                      targets=targets)

    return features, targets, _


class LinearVarModel(RegressorMixin):
    def __init__(self, feature_cols, kernel):
        self.fitted = None
        self.feature_cols = feature_cols
        self.kernel = kernel

    def fit(self, X=pd.DataFrame, y=None):
        features = X[self.feature_cols]
        model = SVR(kernel=self.kernel)
        # features = features.values.reshape(-1)
        model.fit(X=features, y=y.values.reshape(-1, ))

        self.fitted = model

    def predict(self, X: pd.DataFrame):
        features = X[self.feature_cols]
        preds = self.fitted.predict(features)

        return preds

    def get_params(self, deep=False):
        return {'kernel': self.kernel, "feature_cols": self.feature_cols}

    def set_params(self, **parameters):
        self.kernel = parameters['kernel']
        self.feature_cols = parameters['feature_cols']
        return self
