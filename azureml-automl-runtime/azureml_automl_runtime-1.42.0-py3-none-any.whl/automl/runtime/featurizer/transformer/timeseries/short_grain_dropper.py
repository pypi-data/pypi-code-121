# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Drop grains from dataset."""
from typing import Any, List, Optional, cast
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesFeaturizerFitNotCalled,
    TimeseriesInputIsNotTimeseriesDs)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesInsufficientData
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.automl.core.shared.exceptions import ClientException, DataException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.shared.types import GrainType

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer


class ShortGrainDropper(AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer):
    """Drop short series, or series not found in training set."""

    def __init__(self,
                 target_rolling_window_size: int = 0,
                 target_lags: Optional[List[int]] = None,
                 n_cross_validations: Optional[int] = None,
                 cv_step_size: Optional[int] = None,
                 max_horizon: int = TimeSeriesInternal.MAX_HORIZON_DEFAULT,
                 **kwargs: Any) -> None:
        """
        Constructor.

        :param target_rolling_window_size: The size of a target rolling window.
        :param target_lags: The size of a lag of a lag operator.
        :param n_cross_validations: The number of cross validations.
        :param cv_step_size: The number of steps to move validation set.
        :param max_horizon: The maximal horizon.
        :raises: ConfigException
        """
        super().__init__()
        self._grains_to_keep = []  # type: List[GrainType]
        self._short_grains = []  # type: List[GrainType]
        self._has_short_grains = False
        self._window_size = target_rolling_window_size  # type: int
        self._lags = target_lags if target_lags else [0]  # type: List[int]
        self._cv = n_cross_validations  # type: Optional[int]
        self._cv_step_size = cv_step_size    # type: Optional[int]
        self._max_horizon = max_horizon  # type: int
        self._is_fit = False
        self._short_grains_in_train = 0
        self._short_grains_in_train_names = []  # type: List[GrainType]

        # feature flag for inclusion of order column in input dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._no_original_order_column = True

    def _no_original_order_column_safe(self):
        return hasattr(self, '_no_original_order_column') and self._no_original_order_column

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataSet, y: Any = None) -> 'ShortGrainDropper':
        """
        Define the grains to be stored.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to fit on.
        :param y: Ignored
        :raises: DataException
        """
        self._raise_wrong_type_maybe(X, ReferenceCodes._TS_INPUT_IS_NOT_TSDF_SHORT_GRAIN)

        self._short_grains_in_train_names = []
        self._has_short_grains = False
        self._short_grains_in_train = 0
        self._grains_to_keep = []
        min_points = utilities.get_min_points(self._window_size,
                                              self._lags,
                                              self._max_horizon,
                                              self._cv,
                                              self._cv_step_size)
        for grain, df in X.groupby_time_series_id():
            # To mark grain as short we need to use TimeSeriesInternal.DUMMY_ORDER_COLUMN value or
            # if it is not present, the shape of a data frame. The rows where TimeSeriesInternal.DUMMY_ORDER_COLUMN
            # is NaN were not present in the original data set and finally will be removed, leading to error
            # during rolling origin cross validation.
            # UPDATE: Use the missing/row indicator to exclude imputed/filled rows
            keep_grain = True
            row_imputed_name = TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME
            if self._no_original_order_column_safe() and (row_imputed_name in X.data.columns):
                keep_grain = df[row_imputed_name].notnull().sum() >= min_points
            elif TimeSeriesInternal.DUMMY_ORDER_COLUMN in X.data.columns:
                keep_grain = df[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull().sum() >= min_points
            else:
                keep_grain = df.shape[0] >= min_points

            # Mark the grain to keep or drop, depending on if it meets the length threshold
            if keep_grain:
                self._grains_to_keep.append(grain)
            else:
                self._short_grains_in_train_names.append(grain)
                self._has_short_grains = True

        self._short_grains_in_train = len(self._short_grains_in_train_names)

        if not self._grains_to_keep:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(self._short_grains_in_train_names), num_cv=self._cv,
                max_horizon=self._max_horizon, lags=str(self._lags), window_size=self._window_size,
                cv_step_size=self._cv_step_size,
                reference_code=ReferenceCodes._TS_SHORT_GRAINS_ALL_SHORT_REFIT)
            )
        self._is_fit = True
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet, y: Any = None) -> TimeSeriesDataSet:
        """
        Drop grains, which were not present in training set, or were removed.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to check for grains to drop.
        :param y: Ignored
        :raises: ClientException, DataException
        """
        if not self._is_fit:
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_SHORT_GRAINS_NO_FIT_TRANS))
        self._raise_wrong_type_maybe(X, ReferenceCodes._TS_INPUT_IS_NOT_TSDF_SHORT_GRAIN_TRANS)
        drop_grains = set()

        def do_keep_grain(df):
            """Do the filtering and add all values to set."""
            keep = df.name in self._grains_to_keep
            if not keep:
                drop_grains.add(df.name)
            return keep

        result = X.groupby_time_series_id().filter(lambda df: do_keep_grain(df))
        if result.shape[0] == 0:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(list(drop_grains)), num_cv=self._cv,
                max_horizon=self._max_horizon, lags=str(self._lags), window_size=self._window_size,
                cv_step_size=self._cv_step_size,
                reference_code=ReferenceCodes._TS_SHORT_GRAINS_ALL_SHORT_TRANS)
            )
        return X.from_data_frame_and_metadata(result)

    def _raise_wrong_type_maybe(self, X: Any, reference_code: str) -> None:
        """Raise exception if X is not TimeSeriesDataSet."""
        if not isinstance(X, TimeSeriesDataSet):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDs, target='X',
                                    reference_code=reference_code)
            )

    @property
    def grains_to_keep(self) -> List[GrainType]:
        """Return the list of grains to keep."""
        if not self._is_fit:
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_SHORT_GRAINS_NO_FIT_GR))
        return self._grains_to_keep

    @property
    def has_short_grains_in_train(self) -> bool:
        """Return true if there is no short grains in train set."""
        if not self._is_fit:
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_SHORT_GRAINS_NO_FIT_HAS_GR))
        return self._has_short_grains

    @property
    def short_grains_in_train(self) -> int:
        """Return the number of short grains in train."""
        return self._short_grains_in_train

    @property
    def short_grains_in_train_names(self) -> List[GrainType]:
        """Return the list of short grains, removed during training time."""
        return self._short_grains_in_train_names

    @property
    def target_rolling_window_size(self) -> int:
        """Return target window size."""
        return self._window_size

    @property
    def target_lags(self) -> List[int]:
        """Return target lags."""
        return self._lags

    @property
    def n_cross_validations(self) -> Optional[int]:
        """Return number of cv steps."""
        return self._cv

    @property
    def cv_step_size(self) -> Optional[int]:
        """Return the cv step size."""
        return self._cv_step_size

    @property
    def max_horizon(self) -> int:
        """Return forecast horizon."""
        return self._max_horizon
