
class MaxOccurenceModel():
    def __init__(self):
        self.model = 'max_occurence'

    def calibrate(self, X, y):  # , method = 'standard'):
        # no hyper parameter to tune
        pass

    def fit(self, X_train, y_train, X_val, y_val):
        # nothing to do
        pass

    def predict(self, X_test):
        mode_occur = X_test.mode(axis=1)
        y_pred = mode_occur[0].values
        return y_pred

    def get_features_importance(self, features_names):
        run_importances = {}
        # for (name, imp) in zip(features_names, self.model.coef_):
        #     run_importances[name] = imp
        return run_importances