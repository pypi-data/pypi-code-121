# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional, Iterable, cast


from ..constants import FunctionNames
from ..function import Function
from .data_splitting_strategy import AbstractDataSplittingStrategy
from .validation_strategy import AbstractValidationStrategy
from azureml.training.tabular._constants import Tasks
from azureml.training.tabular.score.scoring import score_classification, score_regression, score_forecasting
from azureml.training.tabular.score.constants import CLASSIFICATION_SET, REGRESSION_SET, FORECASTING_SET, \
    REGRESSION_NORMALIZED_SET


class AbstractTask(ABC):
    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy
    ):
        self.metric_name = metric_name
        self.validation_strategy = validation_strategy
        self.data_splitting_strategy = None     # type: Optional[AbstractDataSplittingStrategy]

    @abstractmethod
    def get_scoring_function(self) -> Function:
        raise NotImplementedError

    @property
    def task_type(self) -> str:
        raise NotImplementedError

    @property
    def metric_list(self) -> Iterable[str]:
        raise NotImplementedError

    def get_metrics_list_function(self) -> Function:
        function = Function(FunctionNames.GET_METRICS_NAMES)
        function.add_lines(
            "metrics_names = [",
        )
        for metric in self.metric_list:
            function.add_lines(f"    '{metric}',")
        function.add_lines(
            "]",
            "return metrics_names",
        )
        return function

    def get_cv_split_code(self, split_ratio: Optional[float], n_cross_validations: Optional[int]) -> List[str]:
        return [
            f"cv_splits = _CVSplits(X, y, frac_valid={split_ratio}, CV={n_cross_validations}, is_time_series=False"
            f", task='{self.task_type}')",
        ]


class ClassificationTask(AbstractTask):
    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy,
        data_splitting_strategy: AbstractDataSplittingStrategy
    ):
        self.data_splitting_strategy = data_splitting_strategy
        super().__init__(metric_name, validation_strategy)

    def get_scoring_function(self) -> Function:
        function = Function(
            FunctionNames.CALCULATE_METRICS_NAME, "model", "X", "y", "sample_weights", "X_test", "y_test",
            "cv_splits=None"
        )
        function.add_imports(score_classification)
        function.add_lines(
            "y_pred_probs = model.predict_proba(X_test)",
            "if isinstance(y_pred_probs, pd.DataFrame):",
            "    y_pred_probs = y_pred_probs.values",
            "class_labels = np.unique(y)",
            "train_labels = model.classes_",
            "metrics = score_classification(",
            f"    y_test, y_pred_probs, {FunctionNames.GET_METRICS_NAMES}(), class_labels, train_labels, "
            f"use_binary=True)",
            "return metrics",
        )
        return function

    @property
    def metric_list(self) -> Iterable[str]:
        return cast(Iterable[str], CLASSIFICATION_SET)

    @property
    def task_type(self) -> str:
        return cast(str, Tasks.CLASSIFICATION)


class RegressionTask(AbstractTask):
    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy,
        data_splitting_strategy: AbstractDataSplittingStrategy,
        y_min: Optional[float],
        y_max: Optional[float],
    ):
        self.y_min = y_min
        self.y_max = y_max
        self.data_splitting_strategy = data_splitting_strategy
        super().__init__(metric_name, validation_strategy)

    def get_scoring_function(self) -> Function:
        bin_creation_imports, bin_creation_code = self.validation_strategy.get_bin_creation_code()
        function = Function(
            FunctionNames.CALCULATE_METRICS_NAME, "model", "X", "y", "sample_weights", "X_test", "y_test",
            "cv_splits=None"
        )
        function.add_imports(score_regression)
        function.add_import_tuples(bin_creation_imports)
        function += [
            "y_pred = model.predict(X_test)",
            f"y_min = {self.y_min if self.y_min is not None else 'np.min(y)'}",
            f"y_max = {self.y_max if self.y_max is not None else 'np.max(y)'}",
            "y_std = np.std(y)",
            "",
        ]
        function += bin_creation_code
        function += [
            "metrics = score_regression(",
            f"    y_test, y_pred, {FunctionNames.GET_METRICS_NAMES}(), y_max, y_min, y_std, sample_weights, bin_info)",
            "return metrics",
        ]
        return function

    @property
    def metric_list(self) -> Iterable[str]:
        return cast(Iterable[str], REGRESSION_SET)

    @property
    def task_type(self) -> str:
        return cast(str, Tasks.REGRESSION)


class ForecastingTask(AbstractTask):
    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy,
        y_min: Optional[float],
        y_max: Optional[float]
    ):
        self.y_min = y_min
        self.y_max = y_max
        super().__init__(metric_name, validation_strategy)

    def get_scoring_function(self) -> Function:
        bin_creation_imports, bin_creation_code = self.validation_strategy.get_bin_creation_code()
        function = Function(
            FunctionNames.CALCULATE_METRICS_NAME, "model", "X", "y", "sample_weights", "X_test", "y_test",
            "cv_splits=None"
        )
        function.add_imports(score_regression)
        function.add_imports(score_forecasting)
        function.add_import_tuples(bin_creation_imports)
        function += [
            "y_pred, _ = model.forecast(X_test)",
            f"y_min = {self.y_min if self.y_min is not None else 'np.min(y)'}",
            f"y_max = {self.y_max if self.y_max is not None else 'np.max(y)'}",
            "y_std = np.std(y)",
            "",
        ]
        function += bin_creation_code
        function += [
            f"regression_metrics_names, forecasting_metrics_names = {FunctionNames.GET_METRICS_NAMES}()",
            "metrics = score_regression(",
            "    y_test, y_pred, regression_metrics_names, y_max, y_min, y_std, sample_weights, bin_info)",
            "",
            "try:",
            "    horizons = X_test['horizon_origin'].values",
            "except Exception:",
            "    # If no horizon is present we are doing a basic forecast.",
            "    # The model's error estimation will be based on the overall",
            "    # stddev of the errors, multiplied by a factor of the horizon.",
            "    horizons = np.repeat(None, y_pred.shape[0])",
            "",
            f"featurization_step = {FunctionNames.FEATURIZE_FUNC_NAME}()",
            "grain_column_names = featurization_step.grain_column_names",
            "time_column_name = featurization_step.time_column_name",
            "",
            "forecasting_metrics = score_forecasting(",
            "    y_test, y_pred, forecasting_metrics_names, horizons, y_max, y_min, y_std, sample_weights, bin_info,",
            "    X_test, X, y, grain_column_names, time_column_name)",
            "metrics.update(forecasting_metrics)",

            # TODO: There is a step here that requires normalizing per-grain metrics. (Task 1673093)
            # compute_normalized_metrics_forecasting_by_grain()
            # However it requires that we have an engineered feature names mapping, which we currently don't have in
            # azureml-training-tabular.
            # Until then, REGRESSION_NORMALIZED_SET metrics are removed from the list of metrics we calculate so that
            # we aren't giving bad numbers.

            "return metrics",
        ]

        # Below is the code we need to run for task 1673093
        """
        # Update normalized metrics to be normalized by grain.
        # if the place holder grain column is in grain column lists we have a single grain
        # and can skip the update.
        if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in grain_column_names:
            agg_norm_by_grain = compute_normalized_metrics_forecasting_by_grain(
                X_train,
                y_train,
                X_test,
                y_test,
                y_pred,
                metrics,
                sample_weight,
                transformation_pipeline
            )
            scores.update(agg_norm_by_grain)
        """
        return function

    def get_metrics_list_function(self) -> Function:
        function = Function(FunctionNames.GET_METRICS_NAMES)
        function.add_lines(
            "regression_metrics_names = [",
        )
        # Remove normalized metrics until we can map engineered feature names. task 1673093
        for metric in REGRESSION_SET - REGRESSION_NORMALIZED_SET:
            function.add_lines(f"    '{metric}',")
        function.add_lines(
            "]",
        )
        function.add_lines(
            "forecasting_metrics_names = [",
        )
        for metric in self.metric_list:
            function.add_lines(f"    '{metric}',")
        function.add_lines(
            "]",
        )
        function.add_lines(
            "return regression_metrics_names, forecasting_metrics_names",
        )
        return function

    @property
    def metric_list(self) -> Iterable[str]:
        return cast(Iterable[str], FORECASTING_SET)

    @property
    def task_type(self) -> str:
        return cast(str, Tasks.REGRESSION)
