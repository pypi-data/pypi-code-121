# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility classes and functions used by the transforms sub-package."""
from typing import Any, Dict, Optional, Tuple, Union, cast
from warnings import warn

import numpy as np
import pandas as pd

from ..._diagnostics.azureml_error import AzureMLError
from ..._diagnostics.error_definitions import InvalidArgumentTypeWithCondition, TimeseriesDfInvalidArgForecastHorizon
from ..._diagnostics.reference_codes import ReferenceCodes
from ...timeseries._time_series_data_set import TimeSeriesDataSet
from ...timeseries.forecasting_utilities import get_period_offsets_from_dates
from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT


class OriginTimeMixin:
    """Mixin class for origin time utility methods."""

    def verify_max_horizon_input(self, max_horizon: Union[Dict[Union[Tuple[str], str], int], int]) -> None:
        """
        Verify the validity of max_horizon input.

        It must be either a positive integer or a dictionary where all values
        are positive integers.

        :param max_horizon: Maximum horizon input
        :type max_horizon: int, dict

        :return: None
        """
        if isinstance(max_horizon, dict):
            improper_types = [type(h) for h in max_horizon.values()
                              if not (isinstance(h, int) or
                                      issubclass(type(h), np.integer))]
            if len(improper_types) > 0:
                raise AzureMLError.create(
                    TimeseriesDfInvalidArgForecastHorizon,
                    target="max_horizon",
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_MAX_HORIZON_TP,
                )
            not_positive = [h for h in max_horizon.values() if h <= 0]
            if len(not_positive) > 0:
                raise AzureMLError.create(
                    TimeseriesDfInvalidArgForecastHorizon,
                    target="max_horizon",
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_MAX_HORIZON_VAL,
                )
        elif isinstance(max_horizon, int) or issubclass(type(max_horizon), np.integer):
            if max_horizon <= 0:
                raise AzureMLError.create(
                    TimeseriesDfInvalidArgForecastHorizon,
                    target="max_horizon",
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_MAX_HORIZON_VAL2,
                )
        else:
            raise AzureMLError.create(
                TimeseriesDfInvalidArgForecastHorizon,
                target="max_horizon",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_MAX_HORIZON_TP2,
            )

    def max_horizon_from_key_safe(
        self,
        key: Union[Tuple[str], str],
        max_horizon: Union[Dict[Union[Tuple[str], str], int], int],
        default_horizon: int = 1,
    ) -> int:
        """
        Safely return a maximum horizon in the case when it *might* be a value in a dictionary.

        The use case for this utility is when a max_horizon parameter
        to an origin-time-aware transform is a dictionary that maps
        time-series identifying keys to integer horizons.

        :param key: Dictionary key specifying the horizon to retrieve

        :param max_horizon: Object containing maximum horizons
        :type max_horizon: int, dict

        :param default_horizon:
            Default maximum horizon to return when the key
            isn't in the dictionary or max_horizon has an incompatible type
        :type default_horizon: int

        :return: A maximum horizon
        :rtype: int
        """
        try:
            h_max = max_horizon[key] if isinstance(max_horizon, dict) else max_horizon
        except KeyError:
            warn(('OriginTimeMixin: No maximum horizon set for series ' +
                  '{0}. Defaulting to a horizon of {1}.')
                 .format(key, default_horizon),
                 UserWarning)
            h_max = default_horizon

        if not isinstance(h_max, int):
            try:
                h_max = int(h_max)
            except BaseException:
                warn(('OriginTimeMixin: Maximum horizon for series {0} ' +
                      'is not an integer. Defaulting to a horizon of {1}.')
                     .format(key, default_horizon))
                h_max = default_horizon

        return h_max

    def create_origin_times(
        self,
        X: TimeSeriesDataSet,
        max_horizon: Union[int, Dict[Any, int]],
        freq: Optional[Union[str, pd.DateOffset]] = None,
        origin_time_colname: str = ORIGIN_TIME_COLNAME_DEFAULT,
        horizon_colname: Optional[str] = None,
    ) -> TimeSeriesDataSet:
        """
        Create origin time rows in an input data frame.

        If an origin_time_colname is already set, then this method is just
        a pass through.

        :param X: Input data set to create origin times in.
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :param max_horizon:
            Integer horizons defining the origin times to create.
            Parameter can be a single integer - which indicates a maximum
            horizon to create for all grains - or a dictionary where the keys
            are grain levels and each value is an integer maximum horizon.
        :type max_horizon: int, dict

        :param freq:
            Time series frequency as an offset alias or pandas.tseries.offsets.DateOffset.
            If freq=None, the method attempts to infer it from the input
            data frame
        :type freq: str or pandas.tseries.offsets.DateOffset

        :param origin_time_colname:
            Name of origin time column to create in case origin times
            are not already contained in the input data frame.
            The `origin_time_colname` property of the transform output
            will be set to this parameter value in that case.
            This parameter is ignored if the input data frame contains
            origin times.
        :type origin_time_colname: str

        :return: TimeSeriesDataSet with origin times added
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :raises: AutoMLException
        """
        # Pass-through if origin times are set
        if X.origin_time_column_name is not None:
            warn('OriginTimeMixin: Origin times already set. ' +
                 'Returning original data frame.', UserWarning)

            return X

        # Check freq input. Make sure it's a DateOffset.
        # Try to infer it if its not set
        if freq is None:
            freq = X.infer_freq()

        if not isinstance(freq, pd.DateOffset):
            freq = pd.tseries.frequencies.to_offset(freq)

        # Check max_horizon input
        self.verify_max_horizon_input(max_horizon)

        # Internal function for adding origins for a single horizon.
        # Returns a plain pandas.DataFrame with an origin column
        def add_origins_for_horizon(Xgr: pd.DataFrame, h: Any) -> pd.DataFrame:

            origin_time_col = Xgr.index.get_level_values(X.time_column_name) - h * freq
            data_dict = {origin_time_colname: origin_time_col}
            if horizon_colname is not None:
                data_dict[horizon_colname] = h

            return pd.DataFrame(data_dict, index=Xgr.index)

        # ------------------------------------------------

        # Internal function for adding origins for a single grain
        # Returns a plain pandas data frame with an origin column
        def add_origins_single_grain(gr: Union[str, Tuple[str]], Xgr: pd.DataFrame) -> pd.DataFrame:

            h_max = self.max_horizon_from_key_safe(gr, max_horizon)

            # Concat frames from all horizons
            return pd.concat([add_origins_for_horizon(Xgr, h) for h in range(1, h_max + 1)], sort=False)

        # ------------------------------------------------

        if X.time_series_id_column_names:
            origins_df = X.data.groupby(X.time_series_id_column_names, group_keys=False).apply(
                lambda Xgr: add_origins_single_grain(Xgr.name, Xgr)
            )
        else:
            if not isinstance(max_horizon, int):
                raise AzureMLError.create(
                    InvalidArgumentTypeWithCondition,
                    target="max_horizon",
                    reference_code=ReferenceCodes._TS_TRANS_MAX_HORIZON_TYPE_ERROR,
                    argument="forecast_horizon",
                    actual_type=type(max_horizon),
                    condition_str="no time series id is set",
                    expected_types="int",
                )
            origins_df = add_origins_single_grain("", X.data)

        # Join with original frame (as plain data frame)
        X_df_origins = X.data.merge(origins_df, how="left", left_index=True, right_index=True)

        # Create a time-series data set with metadata
        #  set appropriately
        return TimeSeriesDataSet(
            X_df_origins,
            time_column_name=X.time_column_name,
            time_series_id_column_names=X.time_series_id_column_names,
            origin_time_column_name=origin_time_colname,
            target_column_name=X.target_column_name,
            group_column_names=X.group_column_names,
        )

    def detect_max_horizons_by_grain(
        self, X: TimeSeriesDataSet, freq: Union[str, pd.DateOffset] = None
    ) -> Optional[Union[int, Dict[Union[str, Tuple[str]], int]]]:
        """
        Detect a dictionary of maximum horizons for each grain in with a time index and origin times.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return:
            A dictionary of maximum horizons. The keys are grain identifiers;
            the values are integer horizons.
            If the origin time is not set, this function returns
            None.
        :rtype: typing.Union[dict, int]
        """
        if X.origin_time_column_name is None:
            return None

        # Check freq input.
        # Try to infer it if its not set
        if freq is None:
            freq = X.infer_freq()

        horizons = get_period_offsets_from_dates(
            X.data.index.get_level_values(X.origin_time_column_name), X.time_index, freq
        )
        if not X.time_series_id_column_names:
            return cast(int, horizons.max())

        horizon_series = pd.Series(horizons, index=X.data.index)
        max_horizon_series = horizon_series.groupby(level=X.time_series_id_column_names, group_keys=False).max()

        return cast(Dict[Union[str, Tuple[str]], int], max_horizon_series.to_dict())
