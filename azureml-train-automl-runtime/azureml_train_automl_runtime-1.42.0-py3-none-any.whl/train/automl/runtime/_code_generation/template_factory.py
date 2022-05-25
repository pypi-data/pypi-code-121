# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Optional

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from azureml.training.tabular._constants import Tasks
from .data_featurizer_template import DataFeaturizerTemplate
from .featurizer_template import AbstractFeaturizerTemplate, NoFeaturizerTemplate
from .forecast_dnn_model_template import NamedForecastDnnModelTemplate, SingleForecastDnnModelTemplate
from .model_template import AbstractModelTemplate, NamedSklearnModelTemplate, SingleSklearnModelTemplate
from .preprocessor_template import (
    AbstractPreprocessorTemplate,
    NamedPreprocessorTemplate,
    NoPreprocessorTemplate,
    PreprocessorTemplate,
)
from .timeseries_featurizer_template import DnnTimeSeriesFeaturizerTemplate, TimeSeriesFeaturizerTemplate
from .validation.data_splitting_strategy import (
    AbstractDataSplittingStrategy,
    ClassificationDataSplittingStrategy,
    RegressionDataSplittingStrategy,
)
from .validation.validation_strategy import (
    AbstractValidationStrategy,
    CrossValidationStrategy,
    SeparateValidationDataStrategy,
    SplitTrainingDataStrategy,
    TimeSeriesCrossValidationStrategy
)
from .validation.validation_task import AbstractTask, ClassificationTask, RegressionTask, ForecastingTask
from azureml.automl.runtime.featurization import DataTransformer


class FeaturizerTemplateFactory:
    def select_template(self, pipeline: Any, task_type: str) -> AbstractFeaturizerTemplate:
        if isinstance(pipeline, DataTransformer):
            return DataFeaturizerTemplate(pipeline, task_type)
        elif isinstance(pipeline, Pipeline):
            if DataFeaturizerTemplate.can_handle(pipeline):
                return DataFeaturizerTemplate(pipeline, task_type)
            elif TimeSeriesFeaturizerTemplate.can_handle(pipeline):
                return TimeSeriesFeaturizerTemplate(pipeline)
            elif NoFeaturizerTemplate.can_handle(pipeline):
                return NoFeaturizerTemplate()
        elif DnnTimeSeriesFeaturizerTemplate.can_handle(pipeline):
            return DnnTimeSeriesFeaturizerTemplate(pipeline)
        raise NotImplementedError


class PreprocessorTemplateFactory:
    def select_template(self, pipeline: Pipeline, name: Optional[Any] = None) -> AbstractPreprocessorTemplate:
        if name is not None:
            if NamedPreprocessorTemplate.can_handle(pipeline):
                return NamedPreprocessorTemplate(pipeline, name)
        elif PreprocessorTemplate.can_handle(pipeline):
            return PreprocessorTemplate(pipeline)
        if NoPreprocessorTemplate.can_handle(pipeline):
            return NoPreprocessorTemplate()
        raise NotImplementedError


class ValidationTemplateFactory:
    def select_template(
        self,
        task_type: str,
        metric_name: str,
        has_valid_dataset: bool,
        validation_size: Optional[float],
        n_cross_validations: Optional[int],
        y_min: Optional[float],
        y_max: Optional[float],
        is_timeseries: bool
    ) -> AbstractTask:
        if task_type == ClassificationDataSplittingStrategy.TASK_TYPE:
            data_splitting_strategy = ClassificationDataSplittingStrategy()  # type: AbstractDataSplittingStrategy
        elif task_type == RegressionDataSplittingStrategy.TASK_TYPE:
            data_splitting_strategy = RegressionDataSplittingStrategy()
        else:
            raise NotImplementedError(f"No validation strategy for task '{task_type}'")

        if is_timeseries:
            validation_strategy = TimeSeriesCrossValidationStrategy(
                metric_name, validation_size, n_cross_validations)  # type: AbstractValidationStrategy
        elif has_valid_dataset:
            validation_strategy = SeparateValidationDataStrategy()
        elif n_cross_validations:
            validation_strategy = CrossValidationStrategy(task_type, metric_name, validation_size, n_cross_validations)
        else:
            validation_strategy = SplitTrainingDataStrategy(data_splitting_strategy, validation_size)

        if is_timeseries:
            return ForecastingTask(metric_name, validation_strategy, y_min, y_max)
        elif task_type == Tasks.CLASSIFICATION:
            return ClassificationTask(metric_name, validation_strategy, data_splitting_strategy)
        elif task_type == Tasks.REGRESSION:
            return RegressionTask(metric_name, validation_strategy, data_splitting_strategy, y_min, y_max)

        raise NotImplementedError(f"No task template for task '{task_type}'")


class SingleModelTemplateFactory:
    def select_template(self, model: Any, name: Optional[Any] = None) -> AbstractModelTemplate:
        if isinstance(model, BaseEstimator):
            if name is not None:
                return NamedSklearnModelTemplate(model, name)
            else:
                return SingleSklearnModelTemplate(model)
        elif model.__class__.__name__ in {"ForecastTCNWrapper", "Deep4CastWrapper"}:
            if name is not None:
                return NamedForecastDnnModelTemplate(model, name)
            else:
                return SingleForecastDnnModelTemplate(model)
        raise NotImplementedError


featurizer_template_factory = FeaturizerTemplateFactory()
preprocessor_template_factory = PreprocessorTemplateFactory()
validation_template_factory = ValidationTemplateFactory()
single_model_template_factory = SingleModelTemplateFactory()
