from mlfoundry.enums import ModelType
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.metrics.v1.base_metrics import BaseMetrics
from mlfoundry.metrics.v1.binary_classification_metrics import (
    BinaryClassificationMetrics,
)
from mlfoundry.metrics.v1.multiclass_classification_metrics import (
    MultiClassClassificationMetrics,
)
from mlfoundry.metrics.v1.regression_metrics import RegressionMetrics
from mlfoundry.metrics.v1.timeseries_metrics import TimeSeriesMetrics

MODEL_TYPE_TO_METRIC_CLASS_MAP = {
    ModelType.BINARY_CLASSIFICATION: BinaryClassificationMetrics,
    ModelType.MULTICLASS_CLASSIFICATION: MultiClassClassificationMetrics,
    ModelType.REGRESSION: RegressionMetrics,
    ModelType.TIMESERIES: TimeSeriesMetrics,
}


def get_metrics_calculator(model_type: ModelType, *args, **kwargs) -> BaseMetrics:
    if model_type not in MODEL_TYPE_TO_METRIC_CLASS_MAP:
        raise MlFoundryException(f"metrics computer for {model_type} is not registerd")
    return MODEL_TYPE_TO_METRIC_CLASS_MAP[model_type](*args, **kwargs)
