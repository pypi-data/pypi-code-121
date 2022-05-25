# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azureml.core import _metrics

module_logger = logging.getLogger(__name__)

_metric_type_initializers = {}


class ForecastTableMetric(_metrics.ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(ForecastTableMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = _metrics.AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE


_metric_type_initializers[_metrics.AZUREML_FORECAST_HORIZON_TABLE_METRIC_TYPE] = ForecastTableMetric
