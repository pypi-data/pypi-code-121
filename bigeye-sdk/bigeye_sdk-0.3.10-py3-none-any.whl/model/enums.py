from __future__ import annotations

import enum

# TODO: All of these codes are from semantic and should be in a protobuf somehwere.

from bigeye_sdk.class_ext.enum_ext import EnumExtension
from bigeye_sdk.generated.com.torodata.models.generated import MetricType, PredefinedMetric, PredefinedMetricName


class MetricStatus(EnumExtension):
    HEALTHY = 'HEALTHY'  # Query by this status will contain healthy metrics
    ALERTING = 'ALERTING'  # Query by this status will contain alerting metrics
    UNKNOWN = 'UNKNOWN'  # Query by this status will contain failed and unknown status metrics.


class SimpleMetricType(EnumExtension):
    PREDEFINED = "PREDEFINED"
    TEMPLATE = "TEMPLATE"

    def factory(self, metric_name: str) -> MetricType:

        if self == SimpleMetricType.PREDEFINED:
            mt = MetricType()
            mt.predefined_metric = PredefinedMetric(PredefinedMetricName.from_string(metric_name))
            return mt
        elif self == SimpleMetricType.TEMPLATE:
            raise Exception('Not yet supported for Simple Metric Templates.')

    @classmethod
    def get_simple_metric_type(cls, mt: MetricType) -> SimpleMetricType:
        mtd = mt.to_dict()  # TODO: this is the only way it would work.  beterproto has defaults that create 0 int placeholders.  Works for now but try a new way later.
        if 'templateMetric' in mtd:
            return SimpleMetricType.TEMPLATE
        elif 'predefinedMetric' in mtd:
            return SimpleMetricType.PREDEFINED

    @classmethod
    def get_metric_name(cls, mt: MetricType):
        smt = SimpleMetricType.get_simple_metric_type(mt)
        if smt == SimpleMetricType.PREDEFINED:
            return mt.predefined_metric.metric_name.name
        if smt == SimpleMetricType.TEMPLATE:
            return mt.template_metric.template_name

