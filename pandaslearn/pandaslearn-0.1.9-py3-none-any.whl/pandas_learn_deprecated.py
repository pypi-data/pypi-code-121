import time

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.impute import MissingIndicator  # IterativeImputer
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import train_test_split  # type:ignore
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    OneHotEncoder,
    OrdinalEncoder,
    RobustScaler,
    StandardScaler,
)

from .column_transformer_deprecated import CustomTransformer

all_imputers = {
    "SimpleImputer": SimpleImputer,
    # "IterativeImputer": IterativeImputer,
    "MissingIndicator": MissingIndicator,
    "KNNImputer": KNNImputer,
}

all_normalizers = {
    "StandardScaler": StandardScaler,
    "MaxAbsScaler": MaxAbsScaler,
    "MinMaxScaler": MinMaxScaler,
    "RobustScaler": RobustScaler,
}

all_encoders = {
    "OneHotEncoder": OneHotEncoder,
    "OrdinalEncoder": OrdinalEncoder,
}

# TODO: visualization: add barcharts (plotnine)
# TODO: visualization: add histograms (plotnine)
# TODO: visualization: add scatterplots (plotnine)
# TODO: visualization: add lineplots (plotnine)
# TODO: visualization: add boxplots (plotnine)
# TODO: visualization: add violin plots (plotnine)
# TODO: visualization: add function to change theme (xkcd, ?)
# TODO: add a `geo` namespace (+ feature engineering, plots)
# TODO: add tests against a few standard fixtures (precompute values and
#       test against them)
# TODO: integrate missingno package: functions to only compute/sort nullity
# TODO: integrate missingno package: plotnine functions matching missingno plot
#       (including geo)
# TODO: integrate missingno package: timeseries nullity plots (just plot all
#       timelines with gaps)
# TODO: pandas-profiling has a lot of useful analysis useful for ml. Integrate
#       those (provide textual outcomes like dicts or dfs instead of plot)
# TODO: future integration targets: https://compose.alteryx.com/en/stable/
# TODO: future integration targets: https://featuretools.alteryx.com/en/stable/
# TODO: future integration targets: https://evalml.alteryx.com/en/stable/


@pd.api.extensions.register_dataframe_accessor("ml")
class PandasLearn:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj
        self.steps = []
        self.y_steps = []
        self.roles = {}

    def split_timeseries(self, *, target: str, holdout_size: float = 0.2, gap: int = 30):
        self.X = self._obj.drop(target, axis=1)
        self.y = self._obj[target]
        if self.y.shape[1] == 1:
            self.y = self.y.iloc[:, 0].ravel()

        row_count = self.X.shape[0]
        train_count = int(row_count * (1 - holdout_size))

        self.X_train = self.X.loc[:train_count, :]
        self.X_holdout = self.X.loc[train_count:, :]
        self.y_train = self.y[: train_count + 1]
        self.y_holdout = self.y[train_count:]

        print(f"##################### self.X_train.shape:{self.X_train.shape}")
        print(f"##################### self.X_holdout.shape:{self.X_holdout.shape}")
        print(f"##################### self.y_train.shape:{self.y_train.shape}")
        print(f"##################### self.y_holdout.shape:{self.y_holdout.shape}")

        return self

    def split_default(
        self,
        *,
        target: str,
        holdout_size: float = 0.2,
        random_state: int = 42,
        shuffle: bool = True,
        stratify: str = None,
    ):
        # TODO: check the target column exists
        # TODO: depending on dtype of target, mark the problem as
        #       regression or classification, if the user specifies
        #       it differently, label encoding can be done
        self.X = self._obj.drop(target, axis=1)
        self.y = self._obj[target]
        if self.y.shape[1] == 1:
            self.y = self.y.iloc[:, 0].ravel()
        # TODO: Also allow splitting by using values of a column (in
        #       case the df was produced by combining train and test dfs)
        if stratify is not None:
            stratify = self._obj[stratify]
            # TODO: check the stratify column exists
        self.X_train, self.X_holdout, self.y_train, self.y_holdout = train_test_split(
            self.X,
            self.y,
            test_size=holdout_size,
            random_state=random_state,
            stratify=stratify,
            shuffle=shuffle,
        )
        return self

    def split_none(self, *, target: str):  # TODO: shuffle dataset
        # TODO: check the target column exists
        self.X_train = self._obj.drop(target, axis=1)
        self.y_train = self._obj[target]
        if self.y_train.shape[1] == 1:
            self.y_train = self.y_train.iloc[:, 0].ravel()
        return self

    def check_variance(self, drop_threshold: float = None):
        # TODO: return a dict of {column_name: variance}, drop columns
        #       with variance lower than drop_threshold if it is defined
        #       drop from X_train, X_holdout
        pass

    def train(
        self,
        *,
        target_encoder=OrdinalEncoder(),
        model=None,
        config: dict = None,
        sampling_strategy: str = "default",
    ):
        # TODO: for categorical variables, check if categories in train/test match
        target = self.select_target()
        self.pipeline = Pipeline(steps=self.steps)

        if sampling_strategy == "default":
            self.split_default(target=target)
            self.X_train = self.pipeline.fit_transform(self.X_train)
            self.X_holdout = self.pipeline.transform(self.X_holdout)

        if sampling_strategy is None:
            self.split_none(target=target)
            self.X_train = self.pipeline.fit_transform(self.X_train)

        if sampling_strategy == "timeseries":
            self.split_timeseries(target=target)
            self.X_train = self.pipeline.fit_transform(self.X_train)
            self.X_holdout = self.pipeline.transform(self.X_holdout)

        # TODO: Define encoding behaviour - classification vs regression
        # self.target_encoder = target_encoder
        # self.y_train = target_encoder.fit_transform(self.y_train)
        # self.y_holdout = target_encoder.transform(self.y_holdout)

        random_searcher = RandomizedSearchCV(model, **config)
        self.pipeline.steps.append(("model", random_searcher))

        start = time.time()
        # random_searcher.fit(self.X_train, self.y_train)
        self.pipeline.fit(self.X_train, self.y_train)
        end = time.time()
        self.model = self.pipeline  # random_searcher

        self.model_performance = {
            "time_elapsed": end - start,
            # "best_params": random_searcher.best_params_,
            # "best_score": random_searcher.best_score_,
            "best_params": self.pipeline["model"].best_params_,
            "best_score": self.pipeline["model"].best_score_,
        }
        if sampling_strategy in ["default", "timeseries"]:
            self.model_performance["test_score"] = (self.pipeline.score(self.X_holdout, self.y_holdout),)
        print(self.model_performance)

        return self

    def predict(self, df: pd.DataFrame):
        preds = self.pipeline.predict(df)
        return preds

    def select_all_numerical(self):
        target = self.roles["target"]
        return list(set(self.numerical_ix) - set(target))

    def select_all_categorical(self):
        target = self.roles["target"]
        return list(set(self.categorical_ix) - set(target))

    def select_target(self):
        target = self.roles["target"]
        return target

    def select_columns(self, column: str = None):
        return column

    def assign_role(self, *, role: str, col: str):
        # TODO: self.roles[role] += [col]
        self.roles.update({role: [col]})  # TODO: this is bad, the roles list always gets replaced
        return self

    def step_dropna(self):
        # TODO:
        pass

    def str_to_pipeline(self, expr_: str, global_: dict):
        pipeline = Pipeline(
            steps=[
                (
                    expr_,
                    eval(expr_, global_, {}),
                )
            ]
        )
        return pipeline

    def selector_to_features(self, selector: str):
        selected_features = eval("self." + selector, None, None)  # TODO: unsafe global, local
        return selected_features

    def step_encode(
        self,
        selector: str = "select_all_categorical()",  # TODO: replace with select_target()
        encoder: str = "OrdinalEncoder()",
    ):
        pipeline = self.str_to_pipeline(encoder, all_encoders)
        selected_features = list(self.selector_to_features(selector))
        label = selector + "-" + encoder
        transformer = CustomTransformer(
            tfmr=pipeline,
            columns=selected_features,
        )
        self.steps += [(label, transformer)]
        return self

    def step_normalize(
        self,
        selector: str = "select_all_numerical()",
        normalizer: str = "StandardScaler()",
    ):
        pipeline = self.str_to_pipeline(normalizer, all_normalizers)
        selected_features = list(self.selector_to_features(selector))
        label = selector + "-" + normalizer
        transformer = CustomTransformer(tfmr=pipeline, columns=selected_features)
        self.steps += [(label, transformer)]
        return self

    def step_impute(
        self,
        selector: str = "select_all_numerical()",
        imputer: str = "SimpleImputer()",
    ):
        pipeline = self.str_to_pipeline(imputer, all_imputers)
        selected_features = list(self.selector_to_features(selector))
        print(f"################## selected_features: {selected_features}")
        label = selector + "-" + imputer
        transformer = CustomTransformer(tfmr=pipeline, columns=selected_features)
        self.steps += [(label, transformer)]
        return self
