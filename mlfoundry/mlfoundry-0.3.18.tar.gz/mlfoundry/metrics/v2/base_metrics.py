import abc
import typing

import numpy as np
from pydantic import BaseModel

from mlfoundry.enums import ModelType
from mlfoundry.metrics.v2.utils import get_class_names


class ComputedMetrics(BaseModel):
    model_type: str
    metrics: typing.Dict[str, typing.Any]


class BaseMetrics(abc.ABC):
    @property
    @abc.abstractmethod
    def model_type(self) -> ModelType:
        pass

    @abc.abstractmethod
    def get_metric_name_to_function_map(self) -> typing.Dict[str, typing.Callable]:
        pass

    def validate(
        self,
        predictions,
        actuals,
        prediction_probabilities,
        class_names,
    ):
        pass

    def compute_metrics(
        self,
        predictions=None,
        actuals=None,
        prediction_probabilities=None,
        class_names=None,
    ) -> ComputedMetrics:
        self.validate(
            predictions=predictions,
            actuals=actuals,
            prediction_probabilities=prediction_probabilities,
            class_names=class_names,
        )
        metric_name_to_function_map = self.get_metric_name_to_function_map()

        if class_names is None:
            class_names = get_class_names(predictions=predictions, actuals=actuals)
        elif isinstance(class_names, np.ndarray):
            class_names = class_names.tolist()

        metrics = {}
        for (
            metric_name,
            metric_function,
        ) in metric_name_to_function_map.items():
            metric_value = metric_function(
                predictions=predictions,
                actuals=actuals,
                prediction_probabilities=prediction_probabilities,
                class_names=class_names,
            )
            if metric_value is None:
                continue
            metrics[metric_name] = metric_value

        return ComputedMetrics(model_type=self.model_type.value, metrics=metrics)
