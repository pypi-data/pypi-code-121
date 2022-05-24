from cryptotoolbox.forecasting import preprocessing_features
import numpy as np
import pandas as pd

class AnovaLikeModel():

    def __init__(self, signal_action_type = 'ls', mixing_type = 'mean', number_per_year=252):
        self.model = 'anova_like_model'
        self.columns_to_keep = []
        self.median_values = []
        self.signal_action_type = signal_action_type
        self.mixing_type = mixing_type

    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        self.columns_to_keep = preprocessing_features.get_anova_columns(X_train, y_train)
        X_train = X_train[self.columns_to_keep]
        X_val = X_val[self.columns_to_keep]
        self.median_values = list(X_train[self.columns_to_keep].median().values)

    def predict(self, X_test):
        predictions = (X_test[self.columns_to_keep] >= self.median_values).astype(int)

        if self.signal_action_type == 'lo':
            None
        if self.signal_action_type == 'ls':
            predictions = predictions.replace({0: -1})
        if self.mixing_type == 'mean':
            y_pred = predictions.mean(axis=1)
            return y_pred
        if self.mixing_type == 'max':
            y_pred = predictions.max(axis=1)
            return y_pred


    def get_features_importance(self, features_names):
        run_importances = {}
        # for (name, imp) in zip(features_names, self.model.coef_):
        #     run_importances[name] = imp
        return run_importances