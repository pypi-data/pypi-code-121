from typing import List

from bigeye_sdk.class_ext.enum_ext import StrEnum
from bigeye_sdk.generated.com.torodata.models.generated import PredefinedMetric, PredefinedMetricName

OPS_METRICS: List[PredefinedMetric] = [
    PredefinedMetric(metric_name=PredefinedMetricName.PERCENT_NULL),
    PredefinedMetric(metric_name=PredefinedMetricName.COUNT_NULL),
    PredefinedMetric(metric_name=PredefinedMetricName.PERCENT_EMPTY_STRING),
    PredefinedMetric(metric_name=PredefinedMetricName.PERCENT_DATE_NOT_IN_FUTURE),
    PredefinedMetric(metric_name=PredefinedMetricName.MAX),
    PredefinedMetric(metric_name=PredefinedMetricName.MIN),
    PredefinedMetric(metric_name=PredefinedMetricName.AVERAGE),
    PredefinedMetric(metric_name=PredefinedMetricName.COUNT_DUPLICATES),
    PredefinedMetric(metric_name=PredefinedMetricName.COUNT_DISTINCT),
    # PredefinedMetric(metric_name=PredefinedMetricName.HOURS_SINCE_MAX_TIMESTAMP) TODO Must have function that checks if this is the metric time.
]


class MetricFileType(StrEnum):
    SIMPLE = 'SIMPLE'
    FULL = 'FULL'
