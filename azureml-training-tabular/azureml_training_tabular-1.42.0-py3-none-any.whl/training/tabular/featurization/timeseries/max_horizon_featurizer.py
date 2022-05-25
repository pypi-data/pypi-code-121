# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Augment input data with horizon rows and create a horizon feature."""
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..._diagnostics.azureml_error import AzureMLError
from ..._diagnostics.debug_logging import function_debug_log_wrapped
from ..._diagnostics.error_definitions import DataContainOriginColumn
from ..._diagnostics.reference_codes import ReferenceCodes
from ...timeseries._automl_forecast_freq import AutoMLForecastFreq
from ...timeseries._time_series_data_set import TimeSeriesDataSet
from .._azureml_transformer import AzureMLTransformer
from .forecasting_constants import HORIZON_COLNAME_DEFAULT, ORIGIN_TIME_COLNAME_DEFAULT
from .transform_utils import OriginTimeMixin


class MaxHorizonFeaturizer(AzureMLTransformer, OriginTimeMixin):
    """
    A transformer that adds new rows to a TimeSeriesDataSet up to a maximum forecast horizon
    and also adds an integer-typed horizon column.

    Example:
    >>> raw_data = {'store': ['wholefoods'] * 4,
    ...             'date' : pd.to_datetime(
    ...                   ['2017-01-01', '2017-02-01', '2017-03-01', '2017-04-01']),
    ...             'sales': range(4)}
    >>> tsds = TimeSeriesDataSet(
    ...    data=pd.DataFrame(raw_data),
    ...    time_series_id_column_names=['store'], time_column_name='date',
    ...    target_colun_name='sales')
    >>> tsds
                            sales
        date       store
        2017-01-01 wholefoods      0
        2017-02-01 wholefoods      1
        2017-03-01 wholefoods      2
        2017-04-01 wholefoods      3
    >>> MaxHorizonFeaturizer(2).fit_transform(tsds).data
                                          sales  horizon_origin
        date       store      origin
        2017-01-01 wholefoods 2016-12-01      0               1
                              2016-11-01      0               2
        2017-02-01 wholefoods 2017-01-01      1               1
                              2016-12-01      1               2
        2017-03-01 wholefoods 2017-02-01      2               1
                              2017-01-01      2               2
        2017-04-01 wholefoods 2017-03-01      3               1
                              2017-02-01      3               2
    """

    def __init__(self, max_horizon: int, origin_time_colname: str = ORIGIN_TIME_COLNAME_DEFAULT,
                 horizon_colname: str = HORIZON_COLNAME_DEFAULT,
                 freq: Optional[Union[str, pd.DateOffset]] = None):
        """Create a horizon featurizer."""
        super().__init__()
        self.max_horizon = max_horizon
        self.origin_time_colname = origin_time_colname
        self.horizon_colname = horizon_colname
        self.freq = freq

    def preview_column_names(self, tsds: TimeSeriesDataSet) -> List[str]:
        """
        Get the horizon features name that would be made if the transform were applied to X.

        :param tsds: The TimeSeriesDataSet to generate column names for.
        :type tsds: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :return: horizon feature name
        :rtype: list(str)
        """
        return [self.horizon_colname]

    @property
    def freq(self) -> pd.DateOffset:
        """Return the frequency of the data frame."""
        return self._freq.freq

    @freq.setter
    def freq(self, val: Optional[Union[str, pd.DateOffset]]) -> None:
        """Setter for the frequency."""
        self._freq = AutoMLForecastFreq(val)

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataSet, y: Optional[Any] = None) -> "MaxHorizonFeaturizer":
        """
        Fit the transform.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param y: Ignored. Included for pipeline compatibility
        :return: Fitted transform
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.max_horizon_featurizer.MaxHorizonFeaturizer
        """
        # We can not check self.freq, because of backward compatibility issues.
        if self._freq is None or self._freq.freq is None:
            self._freq = AutoMLForecastFreq(X.infer_freq())

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Create horizon rows and horizon feature.

        If the input already has origin times, an exception is raised.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :return: Data frame with horizon rows and columns
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        """
        if X.origin_time_column_name is not None:
            raise AzureMLError.create(
                DataContainOriginColumn, target="X", reference_code=ReferenceCodes._TSDS_CONTAINS_ORIGIN
            )

        X_new = self.create_origin_times(
            X,
            self.max_horizon,
            freq=self._freq.freq,
            origin_time_colname=self.origin_time_colname,
            horizon_colname=self.horizon_colname,
        )

        return X_new

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params['freq'] = AutoMLForecastFreq._get_freqstr_safe(self)
        return params

    def __setstate__(self, state: Dict[Any, Any]) -> None:
        if not isinstance(state['_freq'], AutoMLForecastFreq):
            state['_freq'] = AutoMLForecastFreq(state['_freq'])
        super().__setstate__(state)
