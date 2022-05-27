"""Base forest-related models using LightGBM as the gradient booster."""
from abc import abstractmethod
import os
from typing import Any, ClassVar, Dict, Optional, Sequence, Tuple, Union, cast

import lightgbm as lgb
from marshmallow import fields
import numpy as np

from bitfount.data.databunch import _BitfountDataBunch
from bitfount.data.dataloaders import _BitfountDataLoader
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.models.base_models import ClassifierMixIn, _BaseModel
from bitfount.types import T_FIELDS_DICT

# TODO: [BIT-1041] Introduce non-implementation base model


class BaseLGBMRandomForest(_BaseModel):
    """Implements an (optionally Gradient Boosted) Random Forest from LightGBM."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "gradient_boosting": fields.Boolean(),
        "num_leaves": fields.Integer(allow_none=True),
        "max_depth": fields.Integer(allow_none=True),
        "subsample_for_bin": fields.Integer(allow_none=True),
        "num_iterations": fields.Integer(allow_none=True),
        "learning_rate": fields.Float(allow_none=True),
        "reg_alpha": fields.Float(allow_none=True),
        "reg_lambda": fields.Float(allow_none=True),
        "bagging_freq": fields.Integer(allow_none=True),
        "bagging_fraction": fields.Float(allow_none=True),
        "feature_fraction": fields.Float(allow_none=True),
        "early_stopping_rounds": fields.Integer(allow_none=True),
        "verbose": fields.Integer(allow_none=True),
        "min_split_gain": fields.Float(allow_none=True),
    }

    def __init__(
        self,
        gradient_boosting: bool = False,
        num_leaves: Optional[int] = None,
        max_depth: Optional[int] = None,
        subsample_for_bin: Optional[int] = None,
        num_iterations: Optional[int] = None,
        learning_rate: Optional[float] = None,
        reg_alpha: Optional[float] = None,
        reg_lambda: Optional[float] = None,
        bagging_freq: Optional[float] = None,
        bagging_fraction: Optional[float] = None,
        feature_fraction: Optional[float] = None,
        early_stopping_rounds: Optional[int] = None,
        verbose: Optional[int] = None,
        min_split_gain: Optional[float] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.model_type = "gbdt" if gradient_boosting is True else "rf"
        self.num_iterations = 10000 if num_iterations is None else num_iterations
        self.learning_rate = 0.05 if learning_rate is None else learning_rate
        self.num_leaves = 50 if num_leaves is None else num_leaves
        self.max_depth = 10 if max_depth is None else max_depth
        self.subsample_for_bin = (
            240000 if subsample_for_bin is None else subsample_for_bin
        )
        self.reg_alpha = 0.5 if reg_alpha is None else reg_alpha
        self.reg_lambda = 0.5 if reg_lambda is None else reg_lambda
        self.bagging_freq = 1 if bagging_freq is None else bagging_freq
        self.bagging_fraction = 0.5 if bagging_fraction is None else bagging_fraction
        self.feature_fraction = 0.5 if feature_fraction is None else feature_fraction
        self.early_stopping_rounds = (
            100 if early_stopping_rounds is None else early_stopping_rounds
        )
        self.verbose = 100 if verbose is None else verbose
        self.min_split_gain = 0.025 if min_split_gain is None else min_split_gain
        self.test_set = None
        self.objective: Optional[str] = None
        self.training_metrics: Optional[Sequence[str]] = None

    @abstractmethod
    def _set_objective(self) -> None:
        """Set training objective."""
        raise NotImplementedError

    @abstractmethod
    def _set_training_metrics(self) -> None:
        """Set training metrics."""
        raise NotImplementedError

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model."""
        self._model.save_model(filename, num_iteration=self._model.best_iteration)

    def deserialize(self, filename: Union[str, os.PathLike]) -> None:
        """Deserialize model."""
        self._model = lgb.Booster(model_file=filename)

    def evaluate(
        self, test_dl: Optional[_BitfountDataLoader] = None, *args: Any, **kwargs: Any
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Perform inference on test set and save dictionary of metrics."""
        if test_dl is None:
            if isinstance(self.test_dl, _BitfountDataLoader):
                test_dl = self.test_dl
            else:
                raise ValueError("There is no test data to evaluate the model on.")

        test_df = test_dl.get_x_dataframe()
        if isinstance(test_df, tuple):
            raise ValueError(
                "Multiple dataframes retrieved unexpectedly; "
                "this model does not support combination tabular and image data."
            )

        test_preds = np.zeros(test_df.shape[0])
        best_iteration = self._model.best_iteration
        test_preds += self._model.predict(test_df, num_iteration=best_iteration)
        test_target = test_dl.get_y_dataframe().to_numpy()

        return test_preds, test_target

    def get_params(self) -> Dict:
        """Create an instance of the model."""
        params = {
            "objective": self.objective,
            "boosting_type": self.model_type,
            "learning_rate": self.learning_rate,
            "num_leaves": self.num_leaves,
            "max_depth": self.max_depth,
            "subsample_for_bin": self.subsample_for_bin,
            "reg_alpha": self.reg_alpha,
            "reg_lambda": self.reg_lambda,
            "min_split_gain": self.min_split_gain,
            "bagging_fraction": self.bagging_fraction,
            "bagging_freq": self.bagging_freq,
            "feature_fraction": self.feature_fraction,
            "random_state": self.seed,
            "metric": self.training_metrics,
            "verbose": self.verbose,
        }

        return params

    def _create_dataset(self) -> Tuple[lgb.Dataset, Optional[lgb.Dataset]]:
        """Create LightGBM Dataset object for better memory management."""
        x_train = self.train_dl.get_x_dataframe()
        if isinstance(x_train, tuple):
            raise ValueError(
                "Multiple dataframes retrieved unexpectedly; "
                "this model does not support combination tabular and image data."
            )

        y_train = self.train_dl.get_y_dataframe().astype("int64")
        train_df = lgb.Dataset(
            data=x_train,
            label=y_train,
            free_raw_data=True,
        )

        weights_col = self.datastructure.loss_weights_col
        if weights_col is not None:
            train_df = train_df.set_weight(weight=list(x_train[weights_col]))
        if isinstance(self.validation_dl, _BitfountDataLoader):
            x_valid = self.validation_dl.get_x_dataframe()
            if isinstance(x_valid, tuple):
                raise ValueError(
                    "Multiple dataframes retrieved unexpectedly; "
                    "this model does not support combination tabular and image data."
                )

            y_valid = self.validation_dl.get_y_dataframe().astype("int64")
            # For LightGBM DataFrame.dtypes for label must be int, float or bool

            validation_df = lgb.Dataset(
                data=x_valid,
                label=y_valid,
                free_raw_data=True,
                reference=train_df,
            )
            if weights_col is not None:
                validation_df = validation_df.set_weight(
                    weight=list(x_valid[weights_col])
                )
        else:
            validation_df = None

        return train_df, validation_df

    def fit(
        self, data: Optional[_BaseSource] = None, *args: Any, **kwargs: Any
    ) -> None:
        """Trains a model using the training set provided by the _BaseSource object."""
        if data:
            if self.datastructure.query:
                table_schema = self.datastructure._override_schema()
                self._databunch = _BitfountDataBunch(
                    data_structure=self.datastructure,
                    schema=table_schema,
                    datasource=data,
                )
            elif self.datastructure.table:
                table_name = self.datastructure.get_table_name()
                table_schema = self.schema.get_table_schema(table_name)
                self._add_datasource_to_schema(data)

            if self.objective == "binary":
                # The casts here are to assuage mypy because it (incorrectly) asserts
                # that a subclass of both ClassifierMixIn and LightGBMModel can't exist.
                # We utilise a subclass of both in the tests to assure ourselves.
                if isinstance(cast(ClassifierMixIn, self), ClassifierMixIn):
                    cast(ClassifierMixIn, self).set_number_of_classes(table_schema)
                else:
                    raise TypeError(
                        "Training objective is classification but this model does not "
                        "inherit from ClassifierMixIn"
                    )
            self._set_dataloaders()

        else:
            raise ValueError(
                "No data provided. This model can only be trained on local data."
            )

        params = self.get_params()
        lgb_train, lgb_valid = self._create_dataset()
        model = lgb.train(
            params=params,
            num_boost_round=self.num_iterations,
            train_set=lgb_train,
            valid_sets=[lgb_valid, lgb_train],
            valid_names=["valid", "train"],
            verbose_eval=self.verbose,
            early_stopping_rounds=self.early_stopping_rounds,
            init_model=self._model,
        )
        self._model: lgb = model
