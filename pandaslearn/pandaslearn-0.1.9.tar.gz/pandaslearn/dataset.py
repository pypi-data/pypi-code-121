from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .column_transformer import CustomFuncTransformer, CustomTransformer
from .definitions import all_encoders, all_imputers, all_normalizers


class TrainingData(BaseModel):
    X_train: Optional[Union[pd.Series, pd.DataFrame]]
    y_train: Optional[Union[pd.Series, pd.DataFrame]]
    X_validation: Optional[Union[pd.Series, pd.DataFrame]]
    y_validation: Optional[Union[pd.Series, pd.DataFrame]]
    X_test: Optional[Union[pd.Series, pd.DataFrame]]
    y_test: Optional[Union[pd.Series, pd.DataFrame]]

    class Config:
        arbitrary_types_allowed = True

    def describe(self):
        out = {}
        if self.X_train is not None:
            out["X_train.shape"] = self.X_train.shape
            out["y_train.shape"] = self.y_train.shape
        if self.X_validation is not None:
            out["X_validation.shape"] = self.X_validation.shape
            out["y_validation.shape"] = self.y_validation.shape
        if self.X_test is not None:
            out["X_test.shape"] = self.X_test.shape
            out["y_test.shape"] = self.y_test.shape
        return out


class Data(BaseModel):
    train: Optional[pd.DataFrame]
    validation: Optional[pd.DataFrame]
    test: Optional[pd.DataFrame]
    submission: Optional[pd.DataFrame]

    class Config:
        arbitrary_types_allowed = True

    def describe(self):
        out = {}
        if self.train is not None:
            out["train.shape"] = self.train.shape
        if self.validation is not None:
            out["validation.shape"] = self.validation.shape
        if self.test is not None:
            out["test.shape"] = self.test.shape
        if self.submission is not None:
            out["submission.shape"] = self.submission.shape

        return out


class Roles(BaseModel):
    target: Optional[str]
    features: Optional[List[str]]
    stratify: Optional[Union[str, pd.Series]]

    class Config:
        arbitrary_types_allowed = True

    def describe(self):
        return {
            "target": self.target,
            "features": self.features,
            "stratify": self.stratify,
        }


class Dataset(BaseModel):
    root: Optional[Union[Path, str]]
    data: Optional[Data]
    training_data: TrainingData = TrainingData()
    roles: Roles = Roles()
    preprocessing_steps: List = []  # TODO: clarify toplogy
    log_cache: List[str] = []
    logger: Any = None

    class Config:
        arbitrary_types_allowed = True

    def add_to_log(self, message: str):
        self.log_cache += [message]

    def log(self, messages: Union[str, List[str]]):
        if isinstance(messages, str):
            messages = [messages]
        if self.logger is None:
            fns = [print, self.add_to_log]
        else:
            fns = [self.logger.logger.info]
        [[fn(message) for fn in fns] for message in messages]

    @property
    def numerical_ix(self) -> List:
        return self.data.test.select_dtypes(
            include=[
                np.number,
                "int64",
                "float64",
            ]
        ).columns.values

    @property
    def categorical_ix(self) -> List:
        return self.data.test.select_dtypes(
            include=[
                "object",
                "bool",
                "category",
            ]
        ).columns.values

    def describe(self):
        output = {}
        if self.data is not None:
            output["data"] = self.data.describe()
        if self.training_data is not None:
            output["training_dataset"] = self.training_data.describe()
        return output

    def check_column_parity(
        self,
        *,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
    ) -> bool:
        cols1 = set(df1.columns)
        cols2 = set(df2.columns)
        if (cols1 - cols2) != set({}):
            print(f"df1 has more columns than df2! difference: {cols1 - cols2}")
            return False
        if (cols2 - cols1) != set({}):
            print(f"df2 has more columns than df1! difference: {cols2 - cols1}")
            return False
        return True

    def get_sample(
        self,
        *,
        frac: float = 0.1,
        replace: bool = False,
        random_state: int = 42,
    ):
        if self.data.train is not None:
            self.data.train = self.data.train.sample(
                frac=frac,
                random_state=random_state,
                replace=replace,
            )
        if self.data.validation is not None:
            self.data.validation = self.data.validation.sample(
                frac=frac,
                random_state=random_state,
                replace=replace,
            )
        if self.data.test is not None:
            self.data.test = self.data.test.sample(
                frac=frac,
                random_state=random_state,
                replace=replace,
            )
        return self

    def drop(self, cols: List[str]):
        for col in cols:
            if col in self.roles.features:
                self.roles.features.remove(col)
            if col in self.roles.target:
                self.roles.target.remove(col)
            if col in self.roles.stratify:
                self.roles.stratify.remove(col)
        if self.data.train is not None:
            self.data.train = self.data.train.drop(cols, axis=1)
        if self.data.validation is not None:
            self.data.validation = self.data.validation.drop(cols, axis=1)
        if self.data.test is not None:
            self.data.test = self.data.test.drop(cols, axis=1)
        return self

    def add_data(self, *, root: Optional[Union[Path, str]] = None):
        if self.root is None and root is None:
            raise ValueError("No root specified!")
        if root is not None:
            self.root = Path(root)
        self.root = Path(self.root)
        self.data = Data(
            train=pd.read_csv(self.root / "train.csv"),
            test=pd.read_csv(self.root / "test.csv"),
            submission=pd.read_csv(self.root / "sample_solution.csv"),
        )
        # self.target = self.train[self.target_str].copy()
        return self

    def add_roles(self, *, role: str, columns: Union[Callable, List[str]]):
        valid_roles = ["target", "features", "stratify"]
        if role not in valid_roles:
            raise ValueError(f"Provided value for role ({role}) not in {valid_roles}")

        # TODO: make it additive instead of replacement
        # (check if role already exsits)
        if isinstance(columns, Callable):
            new_featurelist = columns(self.data.test)
            if isinstance(new_featurelist, List):  # TODO: how to check for List[str]?
                setattr(self.roles, role, new_featurelist)
            else:
                raise ValueError(
                    f"(for role: {role}) Features generated by supplied Callable ({columns}) is not a list (of strings): {new_featurelist}!"
                )
        elif isinstance(columns, List):  # TODO: how to check for List[str]?
            setattr(self.roles, role, columns)
        else:
            raise ValueError(
                f"(for role: {role}) `columns` ({columns}) is not a list (of strings)!"
            )

        return self

    def add_features(
        self,
        func: Callable,
        selector: str = "select_all()",
    ):
        # TODO: Look at Callable annotation to verify if it returns a pd df
        # TODO: raise error if Callable returns df with existing colnames
        # TODO: Have a standard function to check enistence of train+val or train+val+test and raise issues in any other case
        selected_features = list(self.selector_to_features(selector))
        if self.data is not None:
            # TODO: try:except
            # TODO: Check if we are adding the same data (same no of columns, sames column_names) to all dfs
            if self.data.train is not None:
                new_data = func(self.data.train.loc[:, selected_features])
                self.data.train = pd.concat(
                    [self.data.train, new_data],
                    axis=1,
                )
                self.roles.features += new_data.columns.tolist()
                self.roles.features = sorted(self.roles.features)
            if self.data.validation is not None:
                # TODO: try:except
                self.data.validation = pd.concat(
                    [
                        self.data.validation,
                        func(self.data.validation.loc[:, selected_features]),
                    ],
                    axis=1,
                )
            if self.data.test is not None:
                # TODO: try:except
                self.data.test = pd.concat(
                    [
                        self.data.test,
                        func(self.data.test.loc[:, selected_features]),
                    ],
                    axis=1,
                )

        return self

    def remove_features(
        self,
        selector: str = "select_all_categorical()",
    ):
        # TODO: Look at Callable annotation to verify if it returns a pd df
        # TODO: raise error if Callable returns df/List[str] with colnames not in list of existing featuress
        # selected_features = list(self.selector_to_features(selector)).sort()
        pass

    def preprocess_data(self):
        self.data.train["n_missing"] = (
            self.data.train[self.roles.features].isna().sum(axis=1)
        )
        self.data.test["n_missing"] = (
            self.data.test[self.roles.features].isna().sum(axis=1)
        )

        self.data.train["std"] = self.data.train[self.roles.features].std(axis=1)
        self.data.test["std"] = self.data.test[self.roles.features].std(axis=1)

        self.roles.features += ["n_missing", "std"]
        self.roles.features = sorted(self.roles.features)
        self.roles.stratify = self.data.train[
            "n_missing"
        ].copy()  # this is about to be scaled (not int anymore)

        return self

    def select_all(self) -> List[str]:
        return self.roles.features

    def select_all_numerical(self) -> List[str]:
        return list(set(self.roles.features).intersection(set(self.numerical_ix)))

    def select_all_categorical(self) -> List[str]:
        return list(set(self.roles.features).intersection(set(self.categorical_ix)))

    def select_target(self) -> List[str]:
        return self.roles.target

    def select_columns(self, columns: List[str] = []) -> List[str]:
        return list(set(self.roles.features).intersection(set(columns)))

    def select_fn(self, *, fn: Callable) -> List[str]:
        return list(set(self.roles.features).intersection(set(fn(self.data.test))))

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
        selected_features = eval(
            "self." + selector, None, None
        )  # TODO: unsafe global, local
        return list(selected_features)

    def step_encode(
        self,
        selector: str = "select_all_categorical()",
        encoder: str = "OrdinalEncoder()",
    ):
        pipeline = self.str_to_pipeline(encoder, all_encoders)
        selected_features = list(self.selector_to_features(selector)).sort()
        label = selector + "-" + encoder
        transformer = CustomTransformer(
            tfmr=pipeline,
            columns=selected_features,
        )
        self.preprocessing_steps += [(label, transformer)]
        return self

    def step_normalize(
        self,
        selector: str = "select_all_numerical()",
        normalizer: str = "StandardScaler()",
    ):
        pipeline = self.str_to_pipeline(normalizer, all_normalizers)
        selected_features = list(self.selector_to_features(selector))
        label = selector + "-" + normalizer
        transformer = CustomTransformer(
            tfmr=pipeline,
            columns=selected_features,
        )
        self.preprocessing_steps += [(label, transformer)]
        return self

    def step_impute(
        self,
        selector: str = "select_all_numerical()",
        imputer: str = "SimpleImputer()",
    ):
        pipeline = self.str_to_pipeline(imputer, all_imputers)
        selected_features = list(self.selector_to_features(selector))
        label = selector + "-" + imputer
        transformer = CustomTransformer(tfmr=pipeline, columns=selected_features)
        self.preprocessing_steps += [(label, transformer)]
        return self

    def step_func(
        self,
        func: Callable,
        selector: str = "select_all()",
    ):
        selected_features = list(self.selector_to_features(selector))
        label = "fn-" + func.__name__
        transformer = CustomFuncTransformer(func=func, columns=selected_features)
        self.preprocessing_steps += [(label, transformer)]
        return self

    def check_variance(self, drop_threshold: float = None):
        # TODO: return a dict of {column_name: variance}, drop columns
        #       with variance lower than drop_threshold if it is defined
        #       drop from X_train, X_holdout
        pass

    def split_timeseries(
        self,
        *,
        holdout_size: float = 0.2,
        gap: int = 30,
    ):
        # TODO: this is same as split_default()
        # use train_test_split() with shuffle=False
        self.split_none()

        row_count = self.data.train.shape[0]
        train_count = int(row_count * (1 - holdout_size))

        self.training_data.X_validation = self.training_data.X_train.loc[
            train_count:, :
        ]
        self.training_data.y_validation = self.training_data.y_train[train_count:]

        self.training_data.X_train = self.training_data.X_train.loc[:train_count, :]
        self.training_data.y_train = self.training_data.y_train[: train_count + 1]

        return self

    def split_default(
        self,
        *,
        holdout_size: float = 0.2,
        random_state: int = 42,
        shuffle: bool = True,
    ):
        self.split_none()
        # TODO: allow splitting by using values of a column (in
        #       case the df was produced by combining train and test dfs)
        if self.roles.stratify in self.training_data.X_train.columns.values:
            stratify = self.training_data.X_train.loc[:, self.roles.stratify]
        elif self.roles.stratify in self.training_data.y_train.columns.values:
            stratify = self.training_data.y_train.loc[:, self.roles.stratify]
            # TODO: This won't work in multi-label setting

        (
            self.training_data.X_train,
            self.training_data.X_validation,
            self.training_data.y_train,
            self.training_data.y_validation,
        ) = train_test_split(
            self.training_data.X_train,
            self.training_data.y_train,
            test_size=holdout_size,
            random_state=random_state,
            stratify=stratify,
            shuffle=shuffle,
        )
        return self

    def split_none(self):
        """No split into validation or test"""
        # TODO: SELECT ONLY FEATURES and TARGETS
        # TODO: shuffle dataset
        self.training_data.X_train = self.data.train[self.roles.features]  # .copy()
        self.training_data.y_train = self.data.train[self.roles.target].copy()
        if self.training_data.y_train.shape[1] == 1:
            self.training_data.y_train = self.training_data.y_train.iloc[:, 0].ravel()
        return self
