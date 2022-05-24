from cryptotoolbox.forecasting import preprocessing_features
import numpy as np
import pandas as pd

class BaselineModel():

    def __init__(self, threshold = 0.7, signal_action_type ='ls', mixing_type='sum', number_per_year=252):
        self.model = 'simple_model'
        self.threshold = threshold
        self.signal_action_type = signal_action_type
        self.mixing_type = mixing_type
        # self.output_ways = []
        # self.last_avg_return = pd.DataFrame()
        self.median_values = []
        self.way_last_five_avg_return = None
        self.way_last_return = None
        self.weigth_factors = None


    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        self.columns_to_drop = preprocessing_features.most_correlated_features(X_train, self.threshold)
        self.way_last_five_avg_return =y_train[-5:].mean()
        self.way_last_return = np.sign(y_train[-1])
        X_train = X_train.drop(self.columns_to_drop, axis=1)
        X_val = X_val.drop(self.columns_to_drop, axis=1)
        self.median_values = list(X_train.median().values)
        correlation_to_return = preprocessing_features.features_correlation_to_return(X_train,y_train)
        try:
            self.weigth_factors = preprocessing_features.rescalize(correlation_to_return, [min(correlation_to_return), max(correlation_to_return)],[-1, 1])
        except:
            self.weigth_factors = correlation_to_return.copy()
        for i in range(len(self.weigth_factors)):
            if self.way_last_five_avg_return >=0 and self.way_last_return>=0:
                # print('case 1')
                if self.weigth_factors[i]>=0:
                    None
                else:
                    self.weigth_factors[i] = -1*self.weigth_factors[i]
            elif self.way_last_five_avg_return <=0 and self.way_last_return<=0:
                # print('case 2')
                if self.weigth_factors[i] >= 0:
                    self.weigth_factors[i] = -1 * self.weigth_factors[i]
                else:
                    None
            else:
                if self.way_last_five_avg_return >=0 and self.way_last_return<=0:
                    # print('case 3')
                    if self.weigth_factors[i] >= 0:
                        None
                    else:
                        self.weigth_factors[i] = -1 * self.weigth_factors[i]
                else:
                    # print('case 4')
                    # print(self.weigth_factors)
                    if self.weigth_factors[i] >= 0:
                        self.weigth_factors[i] = -1 * self.weigth_factors[i]
                    else:
                        None
        # for daily_feat in X_train.columns:
        #     # print(daily_feat)
        #     # print(f'number of distinct {X[daily_feat].nunique()} values')
        #     self.last_avg_return = pd.DataFrame(pd.DataFrame(y_train[-5:]).mean())
        #     correlation_matrix = np.corrcoef(X_train[daily_feat], y_train)
        #     if (way_last_return>0 and correlation_matrix[0][1]>0):
        #         self.output_ways.append(1)
        #
        #     elif (way_last_return < 0 and correlation_matrix[0][1] < 0):
        #         self.output_ways.append(0)
        #     else:
        #         self.output_ways.append(0.5)

    def predict(self, X_test):
        # X_test = X_test.drop(self.columns_to_drop, axis=1)
        # self.last_avg_return = self.last_avg_return.append([self.last_avg_return] * (len(X_test) - 1), ignore_index=True)
        # next_way = np.max(self.output_ways)
        # if next_way>0:
        #     y_pred = self.last_avg_return
        # elif next_way<0:
        #     y_pred = 0*self.last_avg_return
        # else:
        #     y_pred=0.5*self.last_avg_return
        # return y_pred.values

        X_test = X_test.drop(self.columns_to_drop, axis=1)
        predictions = (X_test >= self.median_values).astype(int)

        if self.signal_action_type == 'lo':
            None
        if self.signal_action_type == 'ls':
            predictions = predictions.replace({0: -1})

        predictions = predictions.multiply(self.weigth_factors, axis=1)
        if self.mixing_type == 'sum':
            y_pred = predictions.sum(axis=1)

        if self.mixing_type == 'mean':
            y_pred = predictions.mean(axis=1)

        y_pred = y_pred.replace([np.inf, -np.inf], np.nan)
        y_pred = y_pred.fillna(0)
        return y_pred
    def get_features_importance(self, features_names):
        run_importances = {}
        # for (name, imp) in zip(features_names, self.model.coef_):
        #     run_importances[name] = imp
        return run_importances