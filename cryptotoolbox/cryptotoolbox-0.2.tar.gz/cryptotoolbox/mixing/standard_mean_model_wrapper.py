import numpy as np

class MeanModel():
    def __init__(self):
        self.model = 'standard_mean'

    def calibrate(self, X, y):  # , method = 'standard'):
        # no hyper parameter to tune
        pass

    def fit(self, X_train, y_train, X_val, y_val):
        # nothing to do
        pass

    def predict(self, X_test):
        y_pred = np.mean(X_test, axis=1).values
        return y_pred

    def get_features_importance(self, features_names):
        run_importances = {}
        # for (name, imp) in zip(features_names, self.model.coef_):
        #     run_importances[name] = imp
        return run_importances