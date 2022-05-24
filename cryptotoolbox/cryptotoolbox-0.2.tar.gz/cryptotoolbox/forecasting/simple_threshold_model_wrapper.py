import numpy as np
import scipy
import pandas as pd
from scipy.stats import linregress

from cryptotoolbox.signal import signal_utility

from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from functools import partial
from numpy.lib.stride_tricks import as_strided as stride
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, minimize
from cryptotoolbox.utility import metrics
import numpy as np
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.connector import crypto_connector
import json

from cryptotoolbox.parallel_run import signal_result_analyzer
from sklearn.metrics import accuracy_score
from functools import partial


class SimpleThresholdModel():

    def __init__(self, lo=False, magnitude=True, transform_features=False, leading_correlations=5,  nb_selected=10, number_per_year=365):
        self.model = None
        self.seed = 0
        self.nb_selected = nb_selected
        self.number_per_year = number_per_year
        self.leading_correlations = leading_correlations
        self.transform_features = transform_features
        self.magnitude = magnitude
        self.lo = lo


    def calibrate(self, X, y):
        return

    def fit(self, X_train, y_train, X_val, y_val):
        print(f'finding the {self.nb_selected} most correlated features with the output')

        X = X_train.copy().fillna(0.)
        y = y_train.copy().fillna(0.)

        output_correlations = []
        leading_output_correlations = []

        for daily_feat in X_train.columns:
            correlation_matrix = np.corrcoef(X[daily_feat], y)
            output_correlations.append(
                {
                    'feature': daily_feat,
                    'correlation': correlation_matrix[0][1]
                }
            )
            leading_correlation_matrix = np.corrcoef(X.iloc[-self.leading_correlations:, X.columns.get_loc(daily_feat)], y.iloc[-self.leading_correlations:])
            leading_output_correlations.append(
                {
                    'feature': daily_feat,
                    'correlation': leading_correlation_matrix[0][1]
                }
            )
        output_correlations_df = pd.DataFrame(output_correlations)
        output_correlations_df['abs_correlation'] = abs(output_correlations_df['correlation'])
        output_correlations_df = output_correlations_df.sort_values(by='abs_correlation', ascending=False)
        output_correlations_df['effect_sign']=np.sign(output_correlations_df['correlation'])
        output_correlations_df.index = output_correlations_df.feature

        leading_output_correlations_df = pd.DataFrame(leading_output_correlations)
        leading_output_correlations_df['abs_correlation'] = abs(leading_output_correlations_df['correlation'])
        leading_output_correlations_df = leading_output_correlations_df.sort_values(by='abs_correlation', ascending=False)
        leading_output_correlations_df['effect_sign'] = np.sign(leading_output_correlations_df['correlation'])
        leading_output_correlations_df.index = leading_output_correlations_df.feature



        selected_output_correlations_df = output_correlations_df.head(self.nb_selected)


        self.selected_features = list(selected_output_correlations_df.feature)

        selected_leading_output_correlations_df = leading_output_correlations_df[leading_output_correlations_df.feature.apply(lambda x: x in self.selected_features) ]

        self.leading_correlation_effects = selected_leading_output_correlations_df['correlation'].to_dict()

        self.correlation_effects = selected_output_correlations_df['correlation'].to_dict()
        selected_X = X[self.selected_features].copy()
        if self.transform_features:
            scaler = StandardScaler()
            scaler.fit(selected_X)
            transformed_selected_X = scaler.transform(selected_X)
            transformed_selected_X_df = pd.DataFrame(data = transformed_selected_X, columns = selected_X.columns, index = selected_X.index)
            self.scaler = scaler
        else :
            transformed_selected_X_df = selected_X.copy()

        past_values_dic = {}
        for feature_to_investigate in self.selected_features:

            x = transformed_selected_X_df[feature_to_investigate].values.copy()
            past_values_dic[feature_to_investigate] = x[:-self.leading_correlations]
        self.past_values_dic = past_values_dic

        return

    def predict(self, X_test):
        X = X_test.copy()
        selected_X = X[self.selected_features].copy()
        if self.transform_features:
            transformed_selected_X = self.scaler.transform(selected_X)
            transformed_selected_X_df = pd.DataFrame(data = transformed_selected_X, columns = selected_X.columns, index = selected_X.index)
        else :
            transformed_selected_X_df = selected_X.copy()
        for feature_to_investigate in self.selected_features:
            #print(feature_to_investigate)
            whole_correlation = self.correlation_effects[feature_to_investigate]
            leading_past_values = self.past_values_dic[feature_to_investigate]
            leading_correlations = self.leading_correlation_effects[feature_to_investigate]

            # long correlation way
            lag_signal_way = np.sign(whole_correlation)
            lead_signal_way = np.sign(leading_correlations)

            x = transformed_selected_X_df[feature_to_investigate].values.copy()
            lead_lag_ar =  x.mean()/leading_past_values.mean()

            lead_lag_correlation_modifier = abs(leading_correlations/whole_correlation)

            # the two signals are in the same way
            # the whole lookback correlation matches the leading correlation
            if lead_signal_way == lag_signal_way:
                #x = x*lag_signal_way*lead_lag_correlation_coefficient
                if self.magnitude:
                    x = x*lag_signal_way*lead_lag_correlation_modifier
                else:
                    x = np.sign(x) * lag_signal_way * lead_lag_correlation_modifier

            else:
                ### the lead does not match the lag
                ### the lead does not match the lag
                ### we go contrarian
                if self.lo:
                    x[:] =  0.
                else:
                    if self.magnitude:
                        x = -x * lag_signal_way * lead_lag_correlation_modifier
                    else:
                        x = -np.sign(x) * lag_signal_way * lead_lag_correlation_modifier


            transformed_selected_X_df[feature_to_investigate]=x
        return transformed_selected_X_df.mean(axis = 1)

    def get_features_importance(self, features_names):
        return
