# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Decompose the target value to the Trend and Seasonality."""
from itertools import product
from typing import Any, Optional, Tuple, List, Callable, Union, Dict, Iterator, cast
import logging

import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import HoltWintersResultsWrapper

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ConflictingValueForArguments,
    GrainAbsent,
    InvalidArgumentType,
    InvalidDampingSettings,
    InvalidForecastDate,
    InvalidForecastDateForGrain,
    InvalidSTLFeaturizerForMultiplicativeModel,
    NoAppropriateEsModel,
    TimeseriesFeaturizerFitNotCalled,
    TimeseriesUnableToDetermineHorizon,
    TimeseriesUnexpectedOrigin,
    StlFeaturizerInsufficientData)
from azureml.automl.core.shared.constants import TimeSeriesInternal, TimeSeries
from azureml.automl.core.shared.exceptions import ConfigException, ClientException, DataException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType

from azureml.automl.runtime._automl_forecast_freq import AutoMLForecastFreq
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.shared import forecasting_utils
from azureml.automl.runtime.shared.forecasting_ts_utils import detect_seasonality_tsdf, get_stl_decomposition

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from .time_series_imputer import TimeSeriesImputer


def _complete_short_series(series_values: np.ndarray,
                           season_len: int) -> Union[np.ndarray, pd.Series]:
    """
    Complete the two seasons required by statsmodels.

    statsmodels requires at least two full seasons of data
    in order to train. "Complete" the data if this requirement
    is not met.
    If there is less than one full season, carry the last observation
    forward to complete a full season.
    Use a seasonal naive imputation to fill in series values
    so the completed series has length at least 2*season_len
    :param series_values: The series with data.
    :type series_values: pd.Series
    :param season_len: The number of periods in the season.
    :type season_len: int
    :returns: the array with extended data or pd.Series.
    :rtype: np.ndarray pr pd.Series

    """
    series_len = len(series_values)

    # Nothing to do if we already have at least two seasons of data
    if series_len >= 2 * season_len:
        return series_values

    if series_len < season_len:
        last_obs = series_values[-1]
        one_season_ext = np.repeat(last_obs, season_len - series_len)
    else:
        one_season_ext = np.array([])

    # Complete a full season
    series_values_ext = np.append(series_values, one_season_ext)

    # Complete the second season via seasonal naive imputation
    num_past_season = len(series_values_ext) - season_len
    series_first_season = series_values_ext[:season_len]
    series_snaive_second_season = series_first_season[num_past_season:]

    # Get the final bit of the series by seasonal naive imputation
    series_snaive_end = series_values_ext[season_len:]

    # Concatenate all the imputations and return
    return np.concatenate((series_values_ext,
                           series_snaive_second_season,
                           series_snaive_end))


def _sm_is_ver9() -> bool:
    """
    Try to determine if the statsmodels version is 0.9.x.

    :returns: True if the statsmodels is of 0.9.x version.
    :rtype: bool

    """
    try:
        import pkg_resources
        sm_ver = pkg_resources.get_distribution('statsmodels').version
        major, minor = sm_ver.split('.')[:2]
        if major == '0' and minor == '9':
            return True
    except BaseException:
        return True

    return False


def _extend_series_for_sm9_bug(series_values: np.ndarray,
                               season_len: int,
                               model_type: Tuple[str, str, bool]) -> np.ndarray:
    """
    Fix the statsmodel 0.9.0 bug.

    statsmodel 0.9.0 has a bug that causes division by zero during
    model fitting under the following condition:
    series_length = num_model_params + 3.
    Try to detect this condition and if it is found, carry the last
    observation forward once in order to increase the series length.
    This bug is fixed in the (dev) version 0.10.x.
    :param series_values: the series with data.
    :type series_values: np.ndarray
    :param season_len: The number of periods in the season.
    :type season_len: int
    :param model_type: The type of a model used.
    :type model_type: tuple

    """
    trend_type, seas_type, damped = model_type
    num_params = 2 + 2 * (trend_type != 'N') + 1 * (damped) + \
        season_len * (seas_type != 'N')

    if len(series_values) == num_params + 3:
        series_ext = cast(np.ndarray, np.append(series_values, series_values[-1]))
    else:
        series_ext = series_values

    return series_ext


class STLFeaturizer(AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer):
    """
    The class for decomposition of input data to the seasonal and trend component.

    If seasonality is not presented by int or np.int64 ConfigException is raised.
    :param seasonality: Time series seasonality. If seasonality is set to -1, it will be inferred.
    :type seasonality: int
    :param seasonal_feature_only: If true, the transform creates a seasonal feature, but not a trend feature.
    :type seasonal_feature_only: bool
    :raises: ConfigException

    """
    SEASONAL_COMPONENT_NAME = 'seasonal'
    TREND_COMPONENT_NAME = 'trend'
    DETECT_SEASONALITY = -1

    def __init__(self,
                 seasonal_feature_only: bool = False,
                 seasonality: Union[int, str] = TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT,
                 freq: Optional[pd.DateOffset] = None) -> None:
        """Constructor."""
        my_seasonality = seasonality
        if seasonality == TimeSeries.AUTO:
            my_seasonality = self.DETECT_SEASONALITY
        if not isinstance(my_seasonality, int):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="seasonality", argument="seasonality",
                    actual_type=type(seasonality), expected_types="int",
                    reference_code=ReferenceCodes._TS_STL_BAD_SEASONALITY)
            )
        super().__init__()
        self.seasonal_feature_only = seasonal_feature_only
        self._seasonality = my_seasonality
        self._stls = {}  # type: Dict[GrainType, Dict[str, np.ndarray]]
        self._es_models = {}  # type: Dict[GrainType, HoltWintersResultsWrapper]

        # We will use an additive Holt-Winters model with no seasonal component to extrapolate trend
        self.es_type = 'AN'
        self.use_boxcox = False
        self.use_basinhopping = False
        self.damped = False
        self.selection_metric = 'aic'
        self._char_to_statsmodels_opt = \
            {'A': 'add', 'M': 'mul', 'N': None}
        self._freq = AutoMLForecastFreq(freq)
        self._first_observation_dates = {}  # type: Dict[GrainType, pd.Timestamp]
        self._last_observation_dates = {}  # type: Dict[GrainType, pd.Timestamp]
        self._sm9_bug_workaround = _sm_is_ver9()
        self._ts_value = None  # type: Optional[str]

    def data_check(self, X: TimeSeriesDataSet) -> None:
        """
        Perform data check before transform will be called.

        If the data are not valid the DataException is being raised.
        :param X: The TimeSeriesDataSet with data to be transformed.
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :raises: DataException
        """
        if X.time_series_id_column_names:
            for grain, df_one in X.data.groupby(X.time_series_id_column_names, group_keys=False):
                if grain not in self._last_observation_dates.keys() or \
                   grain not in self._first_observation_dates.keys():
                    raise DataException._with_error(AzureMLError.create(
                        GrainAbsent, target="grain", grain=grain, reference_code=ReferenceCodes._STL_GRAIN_ABSENT)
                    )
                min_forecast_date = df_one.index.get_level_values(X.time_column_name).min()
                if min_forecast_date < self._first_observation_dates[grain]:
                    raise DataException._with_error(AzureMLError.create(
                        InvalidForecastDateForGrain, target="X", forecast_date=min_forecast_date, grain=str(grain),
                        first_observed_date=self._first_observation_dates[grain],
                        reference_code=ReferenceCodes._STL_INVALID_FORECAST_DATE_GRAIN)
                    )
        else:
            if '' not in self._last_observation_dates.keys() or \
               '' not in self._first_observation_dates.keys():
                raise DataException._with_error(AzureMLError.create(
                    GrainAbsent, target="grain", grain='None',
                    reference_code=ReferenceCodes._STL_GRAIN_ABSENT_NONE)
                )
            min_forecast_date = X.data.index.get_level_values(X.time_column_name).min()
            if min_forecast_date < self._first_observation_dates['']:
                raise DataException._with_error(AzureMLError.create(
                    InvalidForecastDate, target="X", forecast_date=min_forecast_date,
                    first_observed_date=self._first_observation_dates[''],
                    reference_code=ReferenceCodes._STL_INVALID_FORECAST_DATE)
                )

    def _get_imputed_df(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Impute the missing y values.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :rtype: TimeSeriesDataSet

        """
        # Impute values by forward fill the values.
        imputer = TimeSeriesImputer(input_column=cast(str, X.target_column_name),
                                    option='fillna',
                                    method='ffill',
                                    freq=self._freq.freq)
        # We forward filled values at the middle and at the end
        # of a data frame. We will fill the begin with zeroes.
        zero_imputer = TimeSeriesImputer(input_column=cast(str, X.target_column_name),
                                         value=0,
                                         freq=self._freq.freq)
        imputed_X = imputer.transform(X)
        return cast(TimeSeriesDataSet, zero_imputer.transform(imputed_X))

    @function_debug_log_wrapped(logging.INFO)
    def fit(self,
            X: TimeSeriesDataSet,
            y: Optional[np.ndarray] = None) -> 'STLFeaturizer':
        """
        Determine trend and seasonality.

        A DataException is raised if any time-series grains are shorter than the seasonality for the dataframe.
        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.ndarray
        :return: Fitted transform
        :rtype: TimeIndexFeaturizer
        :raises: DataException

        """
        if X.origin_time_column_name is not None:
            raise ClientException._with_error(
                AzureMLError.create(TimeseriesUnexpectedOrigin, target='X',
                                    reference_code=ReferenceCodes._TS_STL_UNEXPECTED_ORIGIN))
        self._ts_value = X.target_column_name
        if self._freq is None or self._freq.freq is None:
            self._freq = AutoMLForecastFreq(X.infer_freq())

        # We have to impute missing values for correct
        # of seasonality detection.
        imputed_X = self._get_imputed_df(X)

        if self.seasonality == self.DETECT_SEASONALITY:
            self._seasonality = detect_seasonality_tsdf(imputed_X)

        if X.time_series_id_column_names:
            for grain, df_one in imputed_X.data.groupby(X.time_series_id_column_names, group_keys=False):
                self._fit_one_grain(grain, X.from_data_frame_and_metadata(df_one))
        else:
            self._fit_one_grain('', X)

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self,
                  X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Create time index features for an input data frame.

        **Note** in this method we assume that we do not know the target value.
        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :return: Data frame with trand and seasonality column.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :raises: ClientException
        """
        if not self._stls.keys() or self.seasonality == self.DETECT_SEASONALITY:
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_STL_NO_FIT))
        self.data_check(X)
        return self._apply_func_to_grains(self._transform_one_grain, X)

    @function_debug_log_wrapped(logging.INFO)
    def fit_transform(self,
                      X: TimeSeriesDataSet,
                      y: Optional[np.ndarray] = None) -> TimeSeriesDataSet:
        """
        Apply `fit` and `transform` methods in sequence.

        **Note** that because in this case we know the target value
        and hence we can use the statsmodel of trend inference.
        :param X: Input data.
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.ndarray
        :return: Data frame with trand and seasonality column.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        """
        self.fit(X)
        return self._apply_func_to_grains(self._fit_transform_one_grain, X)

    def preview_column_names(self,
                             tsds: Optional[TimeSeriesDataSet] = None,
                             target: Optional[str] = None) -> List[str]:
        """
        Return the list of columns to be generated based on data in the data frame X.

        TimeSeriesDataSet or target column, but not both should be provided.
        If neither or both are provided the DataException is raised.
        :param tsds: The TimeSeriesDataSet to generate column names for.
        :type tsds: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param target: The name of a target column.
        :type target: str
        :returns: the list of generated columns.
        :rtype: list
        :raises: DataException

        """
        if (tsds is None or tsds.target_column_name is None) and target is None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="tsds/target", argument_name="tsds/target",
                    reference_code=ReferenceCodes._TST_TSDF_TARGET_NULL
                )
            )

        if (tsds is not None and tsds.target_column_name is not None) and target is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target="tsds/target", arguments=', '.join(['tsds', 'target']),
                    reference_code=ReferenceCodes._TST_TSDF_TARGET_BOTH_PROVIDED
                )
            )

        target_name = tsds.target_column_name if (
            tsds is not None and tsds.target_column_name) else target
        season_name, trend_name = self._get_column_names(cast(str, target_name))

        return [season_name] if self.seasonal_feature_only else [season_name, trend_name]

    def _fit_one_grain(self,
                       grain: GrainType,
                       df_one: TimeSeriesDataSet) -> None:
        """
        Do the STL decomposition of a single grain and save the result object.

        If one of grains contains fewer then one dimensions the DataException is raised.
        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataSet with one grain.
        :type df_one: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :raises: DataException

        """
        self._first_observation_dates[grain] = df_one.time_index.min()
        self._last_observation_dates[grain] = df_one.time_index.max()
        if df_one.data.shape[0] < 2:
            raise DataException._with_error(AzureMLError.create(
                StlFeaturizerInsufficientData, target="X", grain=grain,
                reference_code=ReferenceCodes._STL_INSUFFICIENT_DATA)
            )

        series_vals = cast(pd.Series, df_one.target_values).values
        seasonal, trend, _ = get_stl_decomposition(series_vals, seasonality=self.seasonality)

        self._stls[grain] = {STLFeaturizer.SEASONAL_COMPONENT_NAME: seasonal,
                             STLFeaturizer.TREND_COMPONENT_NAME: trend}
        self._es_models[grain] = self._get_trend_model(trend) \
            if not self.seasonal_feature_only else None

    def _fit_transform_one_grain(self,
                                 grain: GrainType,
                                 df_one: TimeSeriesDataSet) -> pd.DataFrame:
        """
        Infer the seasonality and trend for single grain.

        In this case we assume that fit data are the same as train data.
        This method is used in the fit_transform.
        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataSet with one grain.
        :type df_one: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :returns: The data frame with season and trend columns.
        :rtype: pd.DataFrame
        """
        stl_result = self._stls[grain]
        return self._assign_trend_season(
            df_one, stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME],
            stl_result[STLFeaturizer.TREND_COMPONENT_NAME])

    def _transform_one_grain(self,
                             grain: GrainType,
                             df_one: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Compute seasonality and trend features for a single grain.

        :param grain: the tuple of grains.
        :type grain: tuple
        :param df_one: The TimeSeriesDataSet with one grain.
        :type df_one: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :returns: The data frame with season and trend columns.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        """

        # Define which part of data is in training and which in testing set.
        # The data already present in training set. We know the trend for them.
        df_one_train = None  # type: Optional[TimeSeriesDataSet]
        # The new data, we need to forecast trend.
        df_one_pred = None  # type: Optional[TimeSeriesDataSet]
        # Split the data on training and prediction part.
        if df_one.time_index.min() < self._last_observation_dates[grain]:
            df_one_train = df_one.from_data_frame_and_metadata(
                df_one.data[:self._last_observation_dates[grain]])
        if df_one.time_index.max() > self._last_observation_dates[grain]:
            df_one_pred = df_one.from_data_frame_and_metadata(
                df_one.data[self._last_observation_dates[grain] + to_offset(self.freq):])

        stl_result = self._stls[grain]
        if df_one_train is not None:
            offset = len(
                pd.date_range(
                    self._first_observation_dates[grain],
                    df_one.time_index.min(),
                    freq=self.freq)) - 1
            end = df_one_train.data.shape[0] + offset
            df_one_train = self._assign_trend_season(df_one_train,
                                                     stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME][offset:end],
                                                     stl_result[STLFeaturizer.TREND_COMPONENT_NAME][offset:end])

        if df_one_pred is not None:
            model = self._es_models[grain]
            ts_value = cast(str, self._ts_value)
            season_name, trend_name = self._get_column_names(ts_value)
            try:
                horizon = forecasting_utils.get_period_offsets_from_dates(
                    self._last_observation_dates[grain],
                    df_one_pred.time_index,
                    self.freq).max()
            except KeyError:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesUnableToDetermineHorizon, target='X',
                        ts_id=grain,
                        reference_code=ReferenceCodes._TS_STL_UNDETECTED_HORIZON))

            fcast_start = self._last_observation_dates[grain] + self.freq
            fcast_dates = pd.date_range(start=fcast_start,
                                        periods=horizon,
                                        freq=self.freq)

            seas_comp_train = stl_result[STLFeaturizer.SEASONAL_COMPONENT_NAME]
            if self.seasonality > seas_comp_train.shape[0]:
                # If the seasonality is longer than the length of the training data,
                # impute zeros so there is a full season for the component.
                # In practice, the STL likely returns zeros for the training seasonal component anyway.
                zero_pad_len = self.seasonality - seas_comp_train.shape[0]
                seas_comp_train = np.concatenate([seas_comp_train, np.zeros(zero_pad_len)])

            # Generate seasons for all the time periods beginning from the one next to last
            # date in the training set.
            start_season = len(pd.date_range(start=self._first_observation_dates[grain],
                                             end=self._last_observation_dates[grain],
                                             freq=self.freq)) % self.seasonality
            # Make an array with a single season of data that is in-phase with the input data
            one_season = np.concatenate([seas_comp_train[start_season:self.seasonality],
                                         seas_comp_train[:start_season]])
            nseasons = int(np.ceil(len(fcast_dates) / self.seasonality))
            seasonal = np.tile(one_season, nseasons)[:len(fcast_dates)]

            if model is not None:
                point_fcast = model.forecast(steps=horizon)
            else:
                point_fcast = np.repeat(np.NaN, horizon)
            # Construct the time axis that aligns with the forecasts
            forecast_dict = {
                df_one_pred.time_column_name: fcast_dates,
                season_name: seasonal}
            if not self.seasonal_feature_only:
                forecast_dict.update({trend_name: point_fcast})
            if df_one_pred.time_series_id_column_names:
                forecast_dict.update(forecasting_utils.grain_level_to_dict(
                    df_one_pred.time_series_id_column_names,
                    grain))
            # Merge the data sets and consequently, trim the unused periods.
            tsds_temp = TimeSeriesDataSet(
                pd.DataFrame(forecast_dict),
                time_column_name=df_one_pred.time_column_name,
                time_series_id_column_names=df_one_pred.time_series_id_column_names)
            df_one_pred = df_one_pred.from_data_frame_and_metadata(
                df_one_pred.data.merge(tsds_temp.data, left_index=True, right_index=True))
        if df_one_pred is None:
            # In this case df_one_train have to be not None.
            # This means fit_transform was called.
            return cast(TimeSeriesDataSet, df_one_train)
        if df_one_train is None:
            # In this case df_one_pred have to be not None.
            return df_one_pred
        return df_one_train.concat([df_one_train.data, df_one_pred.data])

    def _assign_trend_season(self,
                             tsds: TimeSeriesDataSet,
                             ar_season: np.ndarray,
                             ar_trend: np.ndarray) -> pd.DataFrame:
        """
        Create the season and trend columns in the data frame.

        :param tsds: Target data frame.
        :type tsds: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param ar_season: seasonality component.
        :type ar_season: np.ndarray
        :param ar_trend: trend component.
        :type ar_trend: np.ndarray
        :returns: The time series data frame with trend and seasonality components.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :raises: DataException

        """
        if self._ts_value is None:
            # This exception should not be raised here,
            # but enforcement of type checking requires Optopnal[str] to be
            # checked for None.
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_STL_NO_FIT_ASSIGN))
        season_name, trend_name = self._get_column_names(self._ts_value)

        assign_dict = {season_name: ar_season}
        if not self.seasonal_feature_only:
            assign_dict[trend_name] = ar_trend
        data = tsds.data.assign(**assign_dict)
        return tsds.from_data_frame_and_metadata(data)

    def _get_column_names(self, target: str) -> Tuple[str, str]:
        """
        Return the names of columns to be generated.

        :param target: The name of a target column.
        :returns: The tuple of seasonality and trend columns.
        :rtype: tuple

        """
        return (target + TimeSeriesInternal.STL_SEASON_SUFFIX,
                target + TimeSeriesInternal.STL_TREND_SUFFIX)

    @property
    def seasonality(self) -> int:
        """
        Return the number of periods after which the series values tend to repeat.

        :returns: seasonality.
        :rtype: int

        """
        return self._seasonality

    @property
    def freq(self) -> pd.DateOffset:
        """Return the frequency."""
        return self._freq.freq

    def _get_trend_model(self,
                         series_values: np.ndarray) -> 'HoltWintersResultsWrapper':
        """
        Train the Exponential Smoothing model on single series.

        This model will be used for the trend forecasting.
        :param series_values: The series with target values.
        :type series_values: np.ndarray
        :returns: The Exponential smoothing model .
        :rtype: HoltWintersResultsWrapper

        """
        # Model type consistency checks
        self._assert_damping_valid()
        self._assert_mult_model_valid(series_values)

        # Make sure the series is long enough for fitting
        # If not, impute values to "complete" the series
        series_values = _complete_short_series(series_values, 1)

        # Internal function for fitting a statsmodel ETS model
        #  and determining if a model type should be considered in selection
        # ------------------------------------------------------------------
        def fit_sm(model_type):
            trend_type, seas_type, damped = model_type

            if self._sm9_bug_workaround:
                series_values_safe = \
                    _extend_series_for_sm9_bug(series_values, 1,
                                               model_type)
            else:
                series_values_safe = series_values

            ets_model = \
                ExponentialSmoothing(series_values_safe,
                                     trend=self._char_to_statsmodels_opt[trend_type],
                                     seasonal=self._char_to_statsmodels_opt[seas_type],
                                     damped=damped,
                                     seasonal_periods=None)

            return ets_model.fit(use_boxcox=self.use_boxcox,
                                 use_basinhopping=self.use_basinhopping)

        def model_is_valid(model_type, has_zero_or_neg):
            trend_type, seas_type, damped = model_type

            if trend_type == 'N' and damped:
                return False

            if (trend_type == 'M' or seas_type == 'M') \
                    and has_zero_or_neg:
                return False

            return True
        # ------------------------------------------------------------------

        # Make a grid of model types and select the one with minimum loss
        has_zero_or_neg = (series_values <= 0.0).any()
        type_grid = self._make_param_grid(False)
        fit_models = {mtype: fit_sm(mtype) for mtype in type_grid
                      if model_is_valid(mtype, has_zero_or_neg)}
        if len(fit_models) == 0:
            raise ClientException._with_error(
                AzureMLError.create(NoAppropriateEsModel,
                                    reference_code=ReferenceCodes._FORECASTING_STL_NO_MODEL,
                                    target='_get_trend_model'))
        best_type, best_result = \
            min(fit_models.items(),
                key=lambda it: getattr(it[1], self.selection_metric))

        return best_result

    def _assert_damping_valid(self) -> None:
        """
        Make sure the damped setting is consistent with the model type setting.

        :raises: ConfigException

        """
        if self.es_type[0] == 'N' and self.damped:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidDampingSettings, target="damping", model_type=self.es_type, is_damped=self.damped,
                    reference_code=ReferenceCodes._TS_STL_BAD_DAMPING
                )
            )

    def _assert_mult_model_valid(self, series_values: pd.Series) -> None:
        """
        Make sure that multiplicative model settings are consistent.

        Currently, the underlying fit cannot handle zero or negative valued
        series with multiplicative models.

        :param series_values: The series with the values.
        :type series_values: pd.Series
        :raises: ConfigException

        """
        if 'M' in self.es_type and (series_values <= 0.0).any():
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidSTLFeaturizerForMultiplicativeModel, target="stl_featurizer", model_type=self.es_type,
                    reference_code=ReferenceCodes._TS_STL_BAD_MUL_MODEL
                )
            )

    def _make_param_grid(self, is_seasonal: bool) -> Iterator[Tuple[str, str, bool]]:
        """
        Make an iterable of model type triples (trend, seasonal, damping).

        :param is_seasonal: Does model include seasonality?
        :type is_seasonal: bool
        :returns: The model grid to be fitted for the best model selection.
        :rtype: list

        """
        mtype = self.es_type
        trend_in, seas_in = mtype
        trend_grid = [trend_in] if trend_in != 'Z' else ['A', 'M', 'N']

        if is_seasonal:
            seasonal_grid = [seas_in] if seas_in != 'Z' else ['A', 'M', 'N']
        else:
            seasonal_grid = ['N']

        damped_grid = [self.damped] \
            if self.damped is not None else [True, False]

        return product(trend_grid, seasonal_grid, damped_grid)

    def _apply_func_to_grains(self,
                              func: 'Callable[[GrainType, TimeSeriesDataSet], TimeSeriesDataSet]',
                              data_frame: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Apply function func to all grains of the data_frame and concatenate their output to another TSDF.

        :param data_frame: The initial data frame.
        :type data_frame: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param func: the function, returning TimeSeriesDataSet and taking grain tuple and
                     TimeSeriesDataSet as a parameters.
        :type func: function
        :param data_frame: target time series data frame.
        :type data_frame: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :returns: The modified data frame.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        """
        if data_frame.time_series_id_column_names:
            result = []
            for grain, X in data_frame.data.groupby(data_frame.time_series_id_column_names, group_keys=False):
                result.append(func(grain, data_frame.from_data_frame_and_metadata(X)).data)
            result_df = data_frame.concat(result)
        else:
            result_df = func('', data_frame)
        result_df.data.sort_index(inplace=True)
        return result_df

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params['freq'] = AutoMLForecastFreq._get_freqstr_safe(self)
        return params

    def __setstate__(self, state: Dict[Any, Any]) -> None:
        if not isinstance(state['_freq'], AutoMLForecastFreq):
            state['_freq'] = AutoMLForecastFreq(state['_freq'])
        AzureMLForecastTransformerBase.__setstate__(self, state)
