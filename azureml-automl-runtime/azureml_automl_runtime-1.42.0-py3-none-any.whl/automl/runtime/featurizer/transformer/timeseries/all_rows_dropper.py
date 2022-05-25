# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The transform, dropping all rows."""
from typing import Optional
import logging

import numpy as np

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesInputIsNotTimeseriesDs
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_base_estimator import (
    AzureMLForecastTransformerBase)


class AllRowsDropper(AzureMLForecastTransformerBase):
    """Drop all rows in TimeSeriesDataSet."""

    def __init__(self):
        """Constructor."""
        # This constructor is needed to comply with scikit-learn notation.
        super().__init__()

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataSet, y: Optional[np.ndarray] = None) -> 'AllRowsDropper':
        """
        Fit is empty for this transform.

        This method is just a pass-through
        :param X: Ignored.
        :param y: Ignored.
        :return: fitted transform.
        """
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Drop all rows of a TimeSeriesDataSet.

        :param X: the input time series data set.
        :return: the empty TimeSeriesDataSet.
        """
        if not isinstance(X, TimeSeriesDataSet):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDs, target='X',
                                    reference_code=ReferenceCodes._TS_INPUT_IS_NOT_TSDF_DROP_ALL)
            )
        return X.from_data_frame_and_metadata(X.data[:0])
