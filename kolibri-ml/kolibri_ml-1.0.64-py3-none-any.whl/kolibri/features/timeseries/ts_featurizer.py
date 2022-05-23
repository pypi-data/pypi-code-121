import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from inspect import getmembers, isfunction
from kolibri.task.timeseries import metrics
from kolibri.features.timeseries.features_utils import (compute_train_features,
#                                                        compute_predict_features,
                                                        compute_lagged_predict_feature,
                                                        parse_window_functions)

from kolibri.features.basefeaturizer import BaseFeaturizer
# disables pandas SettingWithCopyWarning
pd.set_option('mode.chained_assignment', None)

# available time feature
AVAILABLE_TIME_FEATURES = ["year", "quarter", "month", "days_in_month",
                           "year_week", "year_day", "month_day", "week_day",
                           "hour", "minute", "second", "microsecond", "millisecond"
                           "nanosecond", "month_progress", "second_cos", "second_sin",
                           "minute_cos", "minute_sin", "hour_cos", "hour_sin", 
                           "week_day_cos", "week_day_sin", "year_day_cos", "year_day_sin",
                           "year_week_cos", "year_week_sin", "month_cos", "month_sin"]

# available methods in pandas.core.window.Rolling as of pandas 1.0.5
AVAILABLE_RW_FUNCTIONS = ["count", "sum", "mean", "median", "var", "std", "min", 
                          "max", "corr", "cov", "skew", "kurt", "quantile"]

AVAILABLE_METRICS = [member[0].split('_')[1] for member in getmembers(metrics) 
                     if isfunction(member[1])]

class TsFeaturizer(BaseFeaturizer):

    defaults = {
        "fixed":{
            "time-features": [],
            "exclude-features": [],
            "group": [],
            "timestamp":None,
            "window_functions": dict(),
            "n-jobs": -1,
            "add-vars":[],
        },
        "tunable":{
            "lags": {
                "value":[]
            }
        }
            }

    def __init__(self, config):
        super().__init__(config)
        self.model = None

        self.time_features = self.get_parameter("time-features")
        self.exclude_features = ["ds", "y", "y_raw", "weight", "fold_column",
                                 "zero_response"] + self.get_parameter("exclude-features")
        self.ts_uid_columns = self.get_parameter("group")
        self.lags = self.get_parameter("lags")
        self.window_functions = self.get_parameter("window_functions")
        self.n_jobs = self.get_parameter("n-jobs")
        self._validate_inputs()
    
    def _validate_inputs(self):
        """
        Validates the inputs
        """
    
        if not isinstance(self.time_features, list):
            raise TypeError("Parameter 'time_features' should be of type 'list'.")
        else:
            if any([feature not in AVAILABLE_TIME_FEATURES for feature in self.time_features]):
                raise ValueError(f"Values in 'time_features' should by any of: {AVAILABLE_TIME_FEATURES}")
        
        if not isinstance(self.exclude_features, list):
            raise TypeError("Parameter 'exclude_features' should be of type 'list'.")
        
        if not isinstance(self.ts_uid_columns, list):
            raise TypeError("Parameter 'ts_uid_columns' should be of type 'list'.")

        if not isinstance(self.lags, list):
            raise TypeError("Parameter 'lags' should be of type 'list'.")
        else:
            if any([type(x)!=int for x in self.lags]):
                raise ValueError("Values in 'lags' should be integers.")
            elif any([x<1 for x in self.lags]):
                raise ValueError("Values in 'lags' should be integers greater or equal to 1.")
        
        if not isinstance(self.window_functions, dict):
            raise TypeError("Parameter 'window_functions' should be of type dict.")
        else:
            for func_name,rw_config in self.window_functions.items():
                if not isinstance(func_name, str):
                    raise TypeError("Keys in 'window_functions' should by of type str.")
                if isinstance(rw_config, tuple):
                    if len(rw_config) != 3:
                        raise ValueError("Window function tuple should by of size 3.")
                    function,window_shifts,window_sizes = rw_config
                    if function is not None and not callable(function):
                        raise TypeError("Window function tuple 1st value should be None or callable.")
                    if not isinstance(window_shifts, list):
                        raise TypeError("Window function tuple 2nd value should be of type list.")
                    else:
                        if not all([isinstance(window_shift,int) for window_shift in window_shifts]):
                            raise TypeError("Values in window_shifts shoud be of type int.")
                        elif not all([window_shift>=1 for window_shift in window_shifts]):
                            raise ValueError("Values in window_shifts should be equal or greater than 1.")
                    if not isinstance(window_sizes, list):
                        raise TypeError("Window function tuple 3rd value should be of type list.")
                    else:
                        if not all([isinstance(window_size,int) for window_size in window_sizes]):
                            raise TypeError("Values in window_functions shoud be of type int.")
                        elif not all([window_size>1 for window_size in window_sizes]):
                            raise ValueError("Values in window_sizes should be greater than 1.")
                else:
                    raise TypeError("Values in 'window_functions' should be of type tuple.")                
    
    def _validate_input_data(self, train_data, valid_index):
        if not isinstance(train_data, pd.DataFrame):
            raise TypeError("Parameter 'train_data' should be of type pandas.DataFrame.")
        
        if not isinstance(valid_index, pd.Index):
            raise TypeError("Parameter 'valid_index' should be of type 'pandas.Index'.")
        elif not (set(valid_index) <= set(train_data.index)):
            raise ValueError("Parameter 'valid_index' should only contain index values present in 'train_data.index'.") 

        if not (set(self.ts_uid_columns) <= set(train_data.columns) or set(self.ts_uid_columns) <= set(train_data.index.names)):
            raise ValueError(f"Parameter 'train_data' has missing ts_uid_columns: {set(self.ts_uid_columns)-set(train_data.columns)}.")
        
        if {"internal_ts_uid", "_internal_ts_uid"} in set(train_data.columns):
            raise ValueError("Columns 'internal_ts_uid' and '_internal_ts_uid' is reserved for internal usage and can not be in 'train_data' dataframe.")


    def prepare_train_features(self, train_data):
        """
        Parameters
        ----------
        train_data : pandas.DataFrame
            Dataframe with at least columns 'ds' and 'y'.
        """
        train_features = compute_train_features(data=train_data, timestamp_col=self.get_parameter("timestamp"),
                                                target_col=self.target,
                                                ts_uid_columns=self.ts_uid_columns,
                                                time_features=self.time_features,
                                                lags=self.lags,
                                                window_functions=self._window_functions,
                                                ignore_const_cols=True,
                                                n_jobs=self.n_jobs)
        if "zero_response" in train_features.columns:
            train_features = train_features.query("zero_response != 1")

        return train_features

    def prepare_other_features(self, train_data, target):
        """
        Parameters
        ----------
        train_data : pandas.DataFrame
            Dataframe with at least columns 'ds' and 'y'.
        """
        train_features = compute_train_features(data=train_data, timestamp_col=self.get_parameter("timestamp"),
                                                target_col=target,
                                                ts_uid_columns=self.ts_uid_columns,
                                                time_features=self.time_features,
                                                lags=self.lags,
                                                window_functions=self._window_functions,
                                                ignore_const_cols=True,
                                                n_jobs=self.n_jobs)
        if "zero_response" in train_features.columns:
            train_features = train_features.query("zero_response != 1")

        return train_features


    def prepare_features(self, train_data, valid_index=pd.Int64Index([])):
        """
        Parameters
        ----------
        train_data : pandas.DataFrame
            Dataframe with at least columns 'ds' and 'y'.
        valid_index: pandas.Index
            Array with indexes from train_data to be used for validation.
        """
        self._validate_input_data(train_data, valid_index)
        self.raw_train_columns = list(train_data.columns)

        if len(self.ts_uid_columns) == 0:
            # adds a dummy '_internal_ts_uid' column in case of single ts data
            train_data["_internal_ts_uid"] = 0
            self.ts_uid_columns = ["_internal_ts_uid"]
        train_data = train_data.sort_values(self.ts_uid_columns+[self.get_parameter("timestamp")], axis=0)
        
        if len(self.window_functions) > 0:
            self._window_functions = parse_window_functions(self.window_functions)
        else:
            self._window_functions = list()
        

        train_features = self.prepare_train_features(train_data)

        if len(self.get_parameter("add-vars"))>0:
            try:
                other_features=pd.concat([self.prepare_other_features(train_data, feature) for feature in self.get_parameter("add-vars")], axis=1)
                train_features=pd.concat([train_features, other_features], axis=1)
                train_features = train_features.loc[:, ~train_features.columns.duplicated()]

            except Exception as e:
                print(e)
                pass


        self.raw_features = train_features.columns
        self.input_features = [
            feature for feature in train_features.columns
            if feature not in self.exclude_features
            ]
        self.train_data = train_data
        self.train_features = train_features
        self._features_already_prepared = True

        return self.train_features

    def fit(self, train_data, y=None):

        return self.prepare_features(train_data)



