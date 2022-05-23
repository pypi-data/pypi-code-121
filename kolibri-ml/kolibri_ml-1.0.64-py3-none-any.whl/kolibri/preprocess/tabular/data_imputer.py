from kolibri.core.component import Component
from sklearn.impute._base import _BaseImputer, SimpleImputer
import numpy as np
import pandas as pd
from copy import deepcopy
from kolibri.utils.common import prepare_names_for_json
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
from kolibri.preprocess.tabular.time_features_extractor import TimeFeatures
from sklearn.preprocessing import LabelEncoder
import gc

class DataImputer(Component, _BaseImputer):
    """
    Imputes all type of data
      Args:
        Numeric_strategy: string , possible values {'mean','median','zero'}
        categorical_strategy: string , possible values {'not_available','most frequent'}
        target: string , name of the target variable

  """

    defaults = {
        "fixed":{
            "imputer-categorical-strategy": "most-frequent",
            "imputer-numeric-strategy": "median",
            "target": None,
            "missing-value": np.nan,
            "fill-value-numerical" : 0,
            "fill-value-categorical" : "not_available"
        }

    }
    _numeric_strategies = {
        "mean": "mean",
        "median": "median",
        "most frequent": "most_frequent",
        "most_frequent": "most_frequent",
        "zero": "constant",
    }
    _categorical_strategies = {
        "most frequent": "most_frequent",
        "most_frequent": "most_frequent",
        "not_available": "constant",
    }


    def __init__(self, params={}):
        super().__init__(params)

        self.numeric_strategy = self.get_parameter("imputer-numeric-strategy")
        self.target = self.get_parameter("target")
        categorical_strategy=self.get_parameter("imputer-categorical-strategy")
        if self.get_parameter("imputer-categorical-strategy") not in self._categorical_strategies:
            categorical_strategy = "most_frequent"
        self.categorical_strategy = categorical_strategy
        self.numeric_imputer = SimpleImputer(
            strategy=self._numeric_strategies[self.numeric_strategy],
            fill_value=self.get_parameter("fill-value-numerical"),
        )
        self.categorical_imputer = SimpleImputer(
            strategy=self._categorical_strategies[self.categorical_strategy],
            fill_value=self.get_parameter("fill-value-categorical"),
        )
        self.most_frequent_time = []

    def fit(self, dataset, y=None):  #
        try:
            data = dataset.drop(self.target, axis=1)
        except:
            data = dataset
        self.numeric_columns = data.select_dtypes(include=["float32", "int64","float64", "int32"]).columns
        self.categorical_columns = data.select_dtypes(include=["object"]).columns
        self.time_columns = data.select_dtypes(include=["datetime64[ns]"]).columns

        statistics = []

        if not self.numeric_columns.empty:
            self.numeric_imputer.fit(data[self.numeric_columns])
            statistics.append((self.numeric_imputer.statistics_, self.numeric_columns))

        if not self.categorical_columns.empty:
            self.categorical_imputer.fit(data[self.categorical_columns])
            statistics.append(
                (self.categorical_imputer.statistics_, self.categorical_columns)
            )
        if not self.time_columns.empty:
            self.most_frequent_time = []
            for col in self.time_columns:
                self.most_frequent_time.append(data[col].mode()[0])
            statistics.append((self.most_frequent_time, self.time_columns))

        self.statistics_ = np.zeros(shape=len(data.columns), dtype=object)
        columns = list(data.columns)
        for s, index in statistics:
            for i, j in enumerate(index):
                self.statistics_[columns.index(j)] = s[i]

        return

    def transform(self, dataset, y=None):
        data = dataset
        imputed_data = []
        if not self.numeric_columns.empty:
            numeric_data = pd.DataFrame(
                self.numeric_imputer.transform(data[self.numeric_columns]),
                columns=self.numeric_columns,
                index=data.index,
            )
            imputed_data.append(numeric_data)
        if not self.categorical_columns.empty:
            categorical_data = pd.DataFrame(
                self.categorical_imputer.transform(data[self.categorical_columns]),
                columns=self.categorical_columns,
                index=data.index,
            )
            for col in categorical_data.columns:
                categorical_data[col] = categorical_data[col].apply(str)
            imputed_data.append(categorical_data)
        if not self.time_columns.empty:
            time_data = data[self.time_columns]
            for i, col in enumerate(time_data.columns):
                time_data[col].fillna(self.most_frequent_time[i])
            imputed_data.append(time_data)

        if imputed_data:
            data.update(pd.concat(imputed_data, axis=1))
        data.astype(dataset.dtypes)

        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        self.fit(data)
        return self.transform(data)



class IterativeImputer(DataImputer):

    defaults = {
        "fixed":{
            "regressor":None,
            "classifier":None,
            "ordinal-columns":None,
            "max-iter": 10,
            "warm-start":  False,
            "imputation-order":  "ascending",
            "add-indicator":False
        }
    }
    def __init__(self, params ):
        super().__init__(params=params)

        self.regressor = self.get_parameter("regressor")
        self.classifier = self.get_parameter("classifier")
        self.initial_strategy_numeric = self.get_parameter("imputer-numeric-strategy")
        self.initial_strategy_categorical = self.get_parameter("imputer-categorical-strategy")
        self.max_iter = self.get_parameter("max-iter")
        self.warm_start = self.get_parameter("warm-start")
        self.imputation_order = self.get_parameter("imputation-order")

        self.random_state = self.get_parameter("random-state")
        self.target = self.get_parameter("target")
        self.ordinal_columns=self.get_parameter("ordinal-columns")
        if self.ordinal_columns is None:
            self.ordinal_columns = []



    def _impute_one_feature(self, X, column, X_na_mask, fit):

        is_classification = (
            X[column].dtype.name == "object" or column in self.ordinal_columns
        )
        if is_classification:
            if column in self.classifiers_:
                time, dummy, le, estimator = self.classifiers_[column]
            elif not fit:
                return X
            else:
                estimator = deepcopy(self._classifier)
                time = TimeFeatures()
                dummy = DummyConverter({})
                le = LabelEncoder()
        else:
            if column in self.regressors_:
                time, dummy, le, estimator = self.regressors_[column]
            elif not fit:
                return X
            else:
                estimator = deepcopy(self._regressor)
                time = TimeFeatures()
                dummy = DummyConverter({})
                le = None

        if fit:
            fit_kwargs = {}
            X_train = X[~X_na_mask[column]]
            y_train = X_train[column]
            # catboost handles categoricals itself
            if "catboost" not in str(type(estimator)).lower():
                X_train = time.fit_transform(X_train)
                X_train = dummy.fit_transform(X_train)
                X_train.drop(column, axis=1, inplace=True)
            else:
                X_train.drop(column, axis=1, inplace=True)
                fit_kwargs["cat_features"] = []
                for i, col in enumerate(X_train.columns):
                    if X_train[col].dtype.name == "object":
                        X_train[col] = pd.Categorical(
                            X_train[col], ordered=column in self.ordinal_columns
                        )
                        fit_kwargs["cat_features"].append(i)
                fit_kwargs["cat_features"] = np.array(
                    fit_kwargs["cat_features"], dtype=int
                )
            X_train = prepare_names_for_json(X_train)

            if le:
                y_train = le.fit_transform(y_train)

            try:
                assert self.warm_start
                estimator.partial_fit(X_train, y_train)
            except:
                estimator.fit(X_train, y_train, **fit_kwargs)

        X_test = X.drop(column, axis=1)[X_na_mask[column]]
        X_test = time.transform(X_test)
        # catboost handles categoricals itself
        if "catboost" not in str(type(estimator)).lower():
            X_test = dummy.transform(X_test)
        else:
            for col in X_test.select_dtypes("object").columns:
                X_test[col] = pd.Categorical(
                    X_test[col], ordered=column in self.ordinal_columns
                )
        result = estimator.predict(X_test)
        if le:
            result = le.inverse_transform(result)

        if fit:
            if is_classification:
                self.classifiers_[column] = (time, dummy, le, estimator)
            else:
                self.regressors_[column] = (time, dummy, le, estimator)

        if result.dtype.name == "float64":
            result = result.astype("float32")

        X_test[column] = result
        X.update(X_test[column])

        gc.collect()

        return X

    def _impute(self, X, fit: bool):
        if self.target in X.columns:
            target_column = X[self.target]
            X = X.drop(self.target, axis=1)
        else:
            target_column = None

        original_columns = X.columns
        original_index = X.index

        X = X.reset_index(drop=True)
        X = prepare_names_for_json(X)

        self.imputation_sequence_ = (
            X.isnull().sum().sort_values(ascending=self.imputation_order == "ascending")
        )
        self.imputation_sequence_ = [
            col
            for col in self.imputation_sequence_[self.imputation_sequence_ > 0].index
            if X[col].dtype.name != "datetime64[ns]"
        ]

        X_na_mask = X.isnull()

        X_imputed = super().fit_transform(X.copy())

        for i in range(self.max_iter if fit else 1):
            for feature in self.imputation_sequence_:
                X_imputed = self._impute_one_feature(X_imputed, feature, X_na_mask, fit)

        X_imputed.columns = original_columns
        X_imputed.index = original_index

        if target_column is not None:
            X_imputed[self.target] = target_column
        return X_imputed

    def transform(self, X, y=None, **fit_params):
        return self._impute(X, fit=False)

    def fit_transform(self, X, y=None, **fit_params):

        if self.regressor is None:
            raise ValueError("No regressor provided")
        else:
            self._regressor = deepcopy(self.regressor)
        try:
            self._regressor.set_param(random_state=self.get_parameter("random-state"))
        except:
            pass
        if self.classifier is None:
            raise ValueError("No classifier provided")
        else:
            self._classifier = deepcopy(self.classifier)
        try:
            self._classifier.set_param(random_state=self.get_parameter("random-state"))
        except:
            pass

        self.classifiers_ = {}
        self.regressors_ = {}

        return self._impute(X, fit=True)

    def fit(self, X, y=None, **fit_params):
        self.fit_transform(X, y=y, **fit_params)

        return self