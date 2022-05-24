import numpy as np

class WeightedMeanModel():

    def __init__(self):
        self.model = 'to_weighted_mean'

    def calibrate(self, X, y):#, method = 'standard'):
        # no hyper parameter to tune
        pass


    def fit(self, X_train, y_train, X_val, y_val):
        # nothing to do
        pass

    def predict(self, X_test):
        shifted_X_test = X_test.shift(-1)
        # shifted_X_test = shifted_X_test.fillna(0)
        # X_test = X_test.fillna(0)
        turn_over = (X_test - shifted_X_test).fillna(0.)
        inv_turn_over = 1 / (1 + abs(turn_over))
        # inv_turn_over[np.isinf(inv_turn_over)] = 0
        data = inv_turn_over * X_test
        y_pred = np.mean(data, axis=1).values
        return y_pred


    def get_features_importance(self, features_names):
        run_importances = {}
        # for (name, imp) in zip(features_names, self.model.coef_):
        #     run_importances[name] = imp
        return run_importances