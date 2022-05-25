# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities used to infer auto features."""
import datetime
import logging
import math
from typing import cast, List, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd

from statsmodels.tsa import seasonal, stattools
from statsmodels.tsa.tsatools import freq_to_period

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import logging_utilities, utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesCannotInferFrequencyFromTimeIdx,
    TimeseriesFrequencyNotSupported)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesEmptySeries
from azureml.automl.core.shared.constants import TimeSeriesInternal, TimeSeries
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.column_purpose_detection import _time_series_column_helper
from azureml.automl.runtime.shared.types import DataInputType
from pandas.tseries.frequencies import to_offset
from pandas.tseries.offsets import (Minute, Hour, Day, Week,
                                    MonthBegin, MonthEnd,
                                    QuarterBegin, QuarterEnd,
                                    YearBegin, YearEnd, DateOffset)


STL_DECOMPOSITION_ERROR = "Lag and rolling window calculation. STL decomposition. Unknown error."
PACF_ERROR = "Lag and rolling window calculation. Unknown error."
STRONG_SEASONALITY = "Strong seasonality or moving average: de-seasoning did not work well"
DUPLICATED_INDEX = "Duplicated values in time index result in dataset frequency to be 0."
CANNOT_DETECT_FREQUENCY = "Unable to detect frequency for individual time series."

logger = logging.getLogger(__name__)


def get_heuristic_max_horizon(data: pd.DataFrame,
                              time_colname: str,
                              grain_column_names: Optional[List[str]]) -> int:
    """
    Estimate heuristic max horison given the data frame.

    **Note:** If the frequency can not be established the default will be returned.
    :param data: the data frame to estimate heurustics for.
    :time_colname: The name of a time column.
    """
    freq = None
    if grain_column_names is None or grain_column_names == []:
        try:
            freq = get_frequency_safe(data[time_colname])
        except ForecastingDataException:
            logger.info(CANNOT_DETECT_FREQUENCY)
    else:
        # If we have multiple grains we will get the mode frequency.
        freqs = []
        for _, df in data.groupby(grain_column_names):
            try:
                freqs.append(get_frequency_safe(df[time_colname]))
            except ForecastingDataException:
                logger.info(CANNOT_DETECT_FREQUENCY)
        if len(freqs) == 0:
            return TimeSeriesInternal.MAX_HORIZON_DEFAULT
        ddf = pd.DataFrame({'freqs': freqs})
        try:
            # This can fail if we have a mixture of strings
            # and timedeltas. In this case return 1.
            freq = ddf.mode()['freqs'][0]
        except AttributeError:
            return TimeSeriesInternal.MAX_HORIZON_DEFAULT
    if freq is None:
        return TimeSeriesInternal.MAX_HORIZON_DEFAULT
    max_horizon = frequency_based_lags(freq)
    if max_horizon == 0:
        return TimeSeriesInternal.MAX_HORIZON_DEFAULT
    return max_horizon


def get_frequency_safe(time_index: Any) -> pd.DateOffset:
    """
    Determine the frequency of a time index.

    :param time_index: the index, which frequency needs to be determined.
    :return: the frequency value.
    """
    # First convert time_index to date time index.
    try:
        time_index = pd.DatetimeIndex(time_index)
    except Exception as e:
        raise ForecastingDataException(
            "The date time column contains invalid values, "
            "please fix it and run the experiment again. Original error: {}".format(e),
            reference_code='forecasting_heuristic_utils.get_frequency_safe').with_generic_msg(
            'Could not infer the frequency of the time index.')
    time_index = time_index.sort_values()
    try:
        freq = pd.infer_freq(time_index)
    except Exception as e:
        raise ForecastingDataException._with_error(
            AzureMLError.create(
                TimeseriesCannotInferFrequencyFromTimeIdx,
                target='training_data.time_column',
                reference_code=ReferenceCodes._TS_CANNOT_INFER_FREQ_FROM_TIME_IDX,
                time_index=str(time_index),
                ex_info=str(e)
            ), inner_exception=e
        ) from e

    if freq is not None:
        return to_offset(freq)
    diffs = time_index[1:] - time_index[:-1]
    ddf = pd.DataFrame({'diffs': diffs})
    td_ser = ddf.mode()['diffs']
    # Check the case where all values are missing or there is no mode
    if td_ser.empty or pd.isnull(td_ser.iloc[0]):
        err_info = 'Could not find a timedelta mode. The time index may not contain enough valid datetimes.'
        raise ForecastingDataException._with_error(
            AzureMLError.create(TimeseriesCannotInferFrequencyFromTimeIdx,
                                target='training_data.time_column',
                                reference_code=ReferenceCodes._TS_CANNOT_INFER_FREQ_FROM_TIME_IDX_NO_MODE,
                                time_index=str(time_index),
                                ex_info=err_info))

    return timedelta_to_freq_safe(td_ser.iloc[0])


def timedelta_to_freq_safe(delta: pd.Timedelta) -> pd.DateOffset:
    """
    Safely convert pd.Timedelta to pd.DateOffset

    :param delta: The timedelta.
    """
    py_offset = delta.to_pytimedelta()
    if py_offset == datetime.timedelta(0):
        # The time granularity is less then microsecond.
        # Return the zero offset.
        return DateOffset(days=0)
    return pd.tseries.frequencies.to_offset(py_offset)


def frequency_based_lags(freq: pd.DateOffset) -> int:
    """
    Return a frequency based lag that should be added to the list of lags.

    returns 0 if lags can not be estimated.
    :param freq: the frequency for which lags should be determined.
    :return: The value of lags for given frequency or 0.
    """

    tol = 1e-6

    offset = pd.tseries.frequencies.to_offset(freq)

    if isinstance(offset, Minute):
        # see if we evenly divide an hour
        multiple = 3600.0 / offset.delta.total_seconds()
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

        # and if not an hour, do we evenly divide a day?
        multiple = 86400.0 / offset.delta.total_seconds()
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

        return 0

    if isinstance(offset, Hour):
        multiple = 86400.0 / offset.delta.total_seconds()
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

    if isinstance(offset, Day):
        if offset.n == 1:
            return 7
        elif offset.n == 7:
            # Four weeks in the month.
            return 4
        else:
            return 0

    # Fixed lag for the weekly data set.
    if isinstance(offset, Week):
        return 4

    # there is no fixed lag for 'same day last month' due to the above note
    if isinstance(offset, MonthBegin) or isinstance(offset, MonthEnd):
        multiple = 12.0 / offset.n
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)
        return 0

    if isinstance(offset, QuarterBegin) or isinstance(offset, QuarterEnd):
        multiple = 4.0 / offset.n
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)
        return 0

    if isinstance(offset, YearBegin) or isinstance(offset, YearEnd):
        if offset.n == 1:
            return 1
    return 0


def _get_seconds_from_hour_offset_maybe(off: Hour) -> int:
    """
    Pandas does not correctly process multiples of hours in v. 0.23.4

    This function checks if it is the case and corrects it if needed.
    :param off: The hour offset to get seconds from.
    """
    # First check if there is an error.
    test_off = Hour(n=42)
    # we expect 42 * 60 * 60 seconds.
    exp_seconds = 42 * 60 * 60
    # If there is an error 3600 will be returned, which is not 3600 * 42.
    if exp_seconds == test_off.delta.seconds:
        return cast(int, off.delta.seconds)
    else:
        return cast(int, off.n * 60 * 60)


def _log_warn_maybe(msg: str,
                    exception: Optional[BaseException] = None) -> None:
    """
    Function to log warning.

    :param msg: message to log.
    :param exception: exception to log.
    """
    logger.warn(msg)
    if exception is not None:
        logging_utilities.log_traceback(
            exception,
            logger,
            is_critical=False,
            override_error_msg='[Masked as it may contain PII]')


def analyze_pacf_one_grain(series: pd.Series) -> Tuple[Optional[int], Optional[int]]:
    """
    output the suggested lags (p) and rolling window (k) settings

    Input: a DataFrame with one column and a time-based index
    """

    z = 1.96  # 95% significance
    ifreq = None

    if series.index is not None and series.index.freq is None:
        # Fix the series, containing NaNs and/or gaps in dates.
        # For example 01/01/2010, 01/03/2010, 01/04/2010
        # will be filled to
        # 01/01/2010, 01/02/2010, 01/03/2010, 01/04/2010
        # NaNs will be interpolated.
        try:
            ifreq = get_frequency_safe(series.sort_index().index)
        except ForecastingDataException:
            logger.info(CANNOT_DETECT_FREQUENCY)
            return (None, None)
        # find the range of dates within which we should have regular intervals
        mindate = min(series.index)
        maxdate = max(series.index)
        if ifreq + mindate == mindate:
            # The frequency is 0 days which means that we have a duplicated time index.
            _log_warn_maybe(DUPLICATED_INDEX)
            return (None, None)
        # construct the range
        TIME_IX = 'timeidx'
        expected_dates = pd.DataFrame({
            TIME_IX: pd.date_range(mindate, maxdate, freq=ifreq),
            'default': np.NaN
        })
        expected_dates.rename(
            columns={TIME_IX: series.index.names[0]}, inplace=True)
        expected_dates.set_index(series.index.names[0], inplace=True)
        # merge the original series onto the expected times
        series_as_frame = series.to_frame()
        series_as_frame.reset_index(inplace=True, drop=False)
        series_as_frame.set_index(expected_dates.index.names[0], inplace=True, drop=True)
        series_as_frame.columns = ['data']
        filled_out = expected_dates.merge(series_as_frame, how='left', left_index=True, right_index=True)
        # now we have all dates but nan values where rows were not provided
        filled_out = filled_out.drop(columns=['default']).sort_index()
        series = filled_out.interpolate()

    # deseason/detrend the series
    period = -1
    # We should make sure that the series frequency may be converted to periods.
    if ifreq is None:
        ifreq = series.index.freq
        # In this case we did not converted series to data frame
        if isinstance(series, pd.Series):
            series = series.to_frame()
    try:
        # First we try the statsmodels method.
        period = freq_to_period(ifreq)
    except ValueError:
        # If it fails we do our best to fix it.
        period = frequency_based_lags(ifreq)
    if period == 0:
        raise ForecastingDataException._with_error(
            AzureMLError.create(TimeseriesFrequencyNotSupported,
                                target='training_data.time_column',
                                reference_code=ReferenceCodes._TS_FREQUENCY_NOT_SUPPORTED,
                                freq=str(ifreq))
        )

    # Two periods larger than the data period or series length whichever is smaller.
    # TODO: In future it should be the just a series length, but this change needs
    # to be tested for performance.
    lags = min(period * 2, len(series))

    if any([pd.isna(x) for x in series[series.columns[0]]]):
        series = series.interpolate()
        series.dropna(inplace=True, axis=0)
        if len(series) == 0:
            raise DataException._with_error(AzureMLError.create(TimeseriesEmptySeries, target="training_data"))

    # compute pacf, dropping na resulting from STL
    # we will add up the trend and the noise
    try:
        results = seasonal.seasonal_decompose(series, period=period)
        pacf_input_series = (results.trend + results.resid).dropna()
    except ValueError as e:
        msg = "Lag and RW calculation. Series too short. STL decomposition " + \
              "requires a min of 2*freq observations. Calculating PACF using raw data."
        _log_warn_maybe(msg, e)
        pacf_input_series = series
    except BaseException as e:
        msg = STL_DECOMPOSITION_ERROR
        _log_warn_maybe(msg, e)
        pacf_input_series = series

    try:
        pac = stattools.pacf(pacf_input_series, nlags=lags)
    except np.linalg.LinAlgError as e:
        msg = "Linear algebra problem. Might be caused by a constant value series in the data. " + \
              "Or, time series length is too short to estimate PACF for 2*freq of lags."
        _log_warn_maybe(msg, e)
        return (None, None)
    except BaseException as e:
        msg = PACF_ERROR
        _log_warn_maybe(msg, e)
        return (None, None)

    sig = z * 1. / math.sqrt(lags)
    sig_bool = [math.fabs(x) > sig for x in pac]
    if all(sig_bool):
        # warn user there is strong seasonality/moving average
        _log_warn_maybe(STRONG_SEASONALITY)
        p = 0
    else:
        p = np.argmin(sig_bool) - 1  # argmin on bool finds first index where false
        # we want the index of last true
        # 0-based index will account for the first element always being 1
        if p == -1:  # The edge case when the first element is not correlating.
            p = 0

    # argmax will be zero if all are false
    # this will output 1 then and will be ignored
    k = np.argmax(sig_bool[(p + 1):]) + (p + 1)

    return (p, k)


def analyze_pacf_per_grain(dataframe: pd.DataFrame,
                           time_colname: str,
                           target_colname: str,
                           grain_colnames: Optional[Union[str, List[str]]] = None,
                           max_grains: int = 100) -> Tuple[int, int]:
    """
    Analyze all grains in a dataframe and recommend lags and RW settings

    :param dataframe: A DataFrame with the time index in a column.
    :param time_colname: The time column name.
    :param grain_colnames: The grain column names if any.
    :param target_colname: The target column name.
    :max_grains: The maximal number of grains to sample from the data set.
    :return: lags and RW settings.
    """
    dataframe = _time_series_column_helper.convert_to_datetime(dataframe, time_colname)
    INVALID_CORRELATION = "Unable to estimate the PACF. No heuristic lags could be detected." + \
                          "Lags and RW are set to zero."
    DEFAULT_LAG = 0
    DEFAULT_RW = 0
    # get all grain combinations (don't group yet, filter first)
    if grain_colnames is not None:
        grains = dataframe[grain_colnames].drop_duplicates()
        N = grains.shape[0]
        if N >= max_grains:
            # don't use all the grains, but pick 100
            chosen = np.random.choice(N, size=max_grains, replace=False)
        else:
            chosen = range(N)
        chosen_grains = grains.iloc[chosen]
        # If the data frame contains only one grains column,
        if isinstance(chosen_grains, pd.Series):
            chosen_grains = chosen_grains.to_frame()
        subset = dataframe.merge(chosen_grains, how='inner').set_index(time_colname)
        pk = subset.groupby(grain_colnames)[target_colname].apply(lambda x: analyze_pacf_one_grain(x))
        # we now have a series consisting of (p,k) tuples, one tuple per grain
        # unpack into a dataframe and compute the mean
        pk.dropna(inplace=True)
        modes = pd.DataFrame(list(pk), columns=["p", "k"]).mode()
        # If lag imputation fails, set the lag and rolling window size to zero
        if len(modes) == 0:
            _log_warn_maybe(INVALID_CORRELATION)
            modes = {"p": [DEFAULT_LAG], "k": [DEFAULT_RW]}
    else:
        # No grains, only one df.
        p, k = analyze_pacf_one_grain(dataframe.set_index(time_colname)[target_colname])
        if p is None or k is None:
            _log_warn_maybe(INVALID_CORRELATION)
            p = DEFAULT_LAG
            k = DEFAULT_RW
        modes = {"p": [p], "k": [k]}

    Lags = modes["p"][0]
    RW = 0 if Lags == 0 else modes["k"][0]

    return int(Lags), int(RW)


def auto_cv_one_series(grain_length: int,
                       max_horizon: int,
                       lags: List[int],
                       window_size: int,
                       n_cross_validations: Union[int, str],
                       cv_step_size: Union[int, str]) -> Tuple[int, int]:
    """
    output the suggested cv setting (n_cross_validations and cv_step_size)

    Input: a DataFrame with one column and a time-based index
    """
    if isinstance(lags, int):
        lags = [lags]

    # When cv is enabled, get_min_points() = 2 * max_horizon + max(window_size, max(lags)) +
    # (n_cross_validations - 1) * cv_step_size + 2
    tmp = (grain_length - 2 - 2 * max_horizon - max(window_size, max(lags)))
    if n_cross_validations == TimeSeries.AUTO and cv_step_size == TimeSeries.AUTO:
        # We start with n_cross_validations = 5 and cv_step_size = max_horizon, and if grain is too short,
        # decrease cv_step_size to the maximum integer the grain length could support until 1,
        # then do the same thing for n_cross_validations until 2, and leave it to short grain handling after that,
        # as n_cross_validations = 2 and cv_step_size = 1 is the minimal requirements for cv to work.
        cv_step_size = max_horizon
        n_cross_validations = 5
        if tmp / cv_step_size < 4:
            cv_step_size = math.floor(
                tmp / (n_cross_validations - 1))
            if cv_step_size < 1:
                cv_step_size = 1
                n_cross_validations = max(math.floor(
                    tmp / cv_step_size), 2)

    elif isinstance(n_cross_validations, int) and cv_step_size == TimeSeries.AUTO:
        # Similar logic here. First try cv_step_size = max_horizon, and if grain is too short,
        # decrease cv_step_size to the largest integer the grain can can support until 1,
        # as it has reached the minimum cv step size possible.
        cv_step_size = max(
            min(
                math.floor(
                    tmp / (n_cross_validations - 1)
                ),
                max_horizon
            ),
            1
        )
    elif n_cross_validations == TimeSeries.AUTO and isinstance(cv_step_size, int):
        # First try n_cross_validations = 5, and if grain is too short, decrease to the largest integer the grain
        # could support until , and then leave it to short grain handling, as we have reached the minimum of
        # n_cross_validations.
        n_cross_validations = 5
        if tmp / cv_step_size < 5:
            n_cross_validations = max(math.floor(
                tmp / cv_step_size), 2)

    return (int(n_cross_validations), int(cv_step_size))


def auto_cv_per_series(dataframe: pd.DataFrame,
                       time_colname: str,
                       target_colname: str,
                       max_horizon: int,
                       lags: List[int],
                       window_size: int,
                       n_cross_validations: Union[int, str],
                       cv_step_size: Union[int, str],
                       short_grain_handling_config: Optional[str],
                       grain_colnames: Optional[Union[str, List[str]]] = None) -> Tuple[int, int]:
    """
    Recommend n_cross_validations and cv_step_size according to all grains in a dataframe, and
    short_grain_handling settings.

    :param dataframe: A DataFrame with the time index in a column.
    :param time_colname: The time column name.
    :param grain_colnames: The grain column names if any.
    :param target_colname: The target column name.
    :max_grains: The maximal number of grains to sample from the data set.
    :return: n_cross_validations and cv_step_size.
    """
    dataframe = _time_series_column_helper.convert_to_datetime(dataframe, time_colname)
    n_cv_user_set = isinstance(n_cross_validations, int)

    # get all grain combinations (don't group yet, filter first)
    if grain_colnames is not None and grain_colnames != []:
        # If the data frame contains only one grains column,
        if isinstance(grain_colnames, str):
            grain_colnames = [grain_colnames]
        data_frame = dataframe.set_index(time_colname)

        # In the case of "auto" or "drop" in short grain handling, we want to set the cv params
        # according to the shortest grain length that is no shorter than the minimum requirement.
        if short_grain_handling_config == 'auto' or short_grain_handling_config == 'drop':
            min_cv_length = 2 * max_horizon + max(window_size, max(lags)) + (2 - 1) * 1 + 2
            all_grain_lengths = data_frame.groupby(grain_colnames)[target_colname].count().values
            min_req_grains = [x for x in all_grain_lengths if x >= min_cv_length]
            grain_length = min(min_req_grains) if len(min_req_grains) > 0 else min_cv_length
        # In the case of "pad" or "None", we want to set the cv params with the shortest grain length.
        else:
            grain_length = min(data_frame.groupby(grain_colnames, dropna=False)[target_colname].count().values)
        n_cross_validations, cv_step_size = auto_cv_one_series(grain_length, max_horizon, lags, window_size,
                                                               n_cross_validations, cv_step_size)

    else:
        # No grains, only one df.
        grain_length = len(dataframe.set_index(time_colname)[target_colname])
        n_cross_validations, cv_step_size = auto_cv_one_series(grain_length,
                                                               max_horizon, lags, window_size,
                                                               n_cross_validations, cv_step_size)
    if ((short_grain_handling_config == 'drop' or short_grain_handling_config is None)
       and not n_cv_user_set
       and grain_length < utilities.get_min_points(window_size, lags, max_horizon, n_cross_validations, cv_step_size)):
        n_cross_validations = 2

    return int(n_cross_validations), int(cv_step_size)


def try_get_auto_parameters(automl_settings: AutoMLBaseSettings,
                            X: DataInputType,
                            y: DataInputType) -> Tuple[List[int], int, int, Optional[int], Optional[int]]:
    """
    Return the parameters which should be estimated heuristically.

    Now 01/28/2022 it is lags, window_size, max_horizon, n_cross_validations and cv_step_size.
    :param automl_settings: The settings of the run.
    :param X: The input data frame. If the type of input is not a data frame no heursitics will be estimated.
    :param y: The expected data.
    :return: The tuple, cotaining the list of lags, target rolling window size, maximal horizon,
             n_cross_validations and cv_step_size.
    """
    # quick check of the data, no need of tsdf here.
    window_size = automl_settings.window_size if automl_settings.window_size is not None else 0
    lags = automl_settings.lags[TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
        if automl_settings.lags is not None else [0]  # type: List[Union[str, int]]
    # We need to get the heuristics to estimate the minimal number of points needed for training.
    max_horizon = automl_settings.max_horizon
    n_cross_validations = automl_settings.n_cross_validations
    cv_step_size = automl_settings.cv_step_size

    if not isinstance(X, pd.DataFrame):
        # No heuristics is possible.
        # This will lead to more sensible error from TimeSeriesTransformer.
        if window_size == TimeSeries.AUTO:
            window_size = cast(int, TimeSeriesInternal.WINDOW_SIZE_DEFAULT)\
                if TimeSeriesInternal.WINDOW_SIZE_DEFAULT is not None else 0
        if lags == [TimeSeries.AUTO]:
            lags = [0] if TimeSeriesInternal.TARGET_LAGS_DEFAULT is None else [
                TimeSeriesInternal.TARGET_LAGS_DEFAULT]
        if max_horizon == TimeSeries.AUTO:
            max_horizon = TimeSeriesInternal.MAX_HORIZON_DEFAULT
        if n_cross_validations is not None:
            if n_cross_validations == TimeSeries.AUTO:
                n_cross_validations = TimeSeriesInternal.CROSS_VALIDATIONS_DEFAULT_NON_AUTO
            if cv_step_size == TimeSeries.AUTO:
                cv_step_size = TimeSeriesInternal.CV_STEP_SIZE_DEFAULT_NON_AUTO
            n_cross_validations = cast(int, n_cross_validations)
        if cv_step_size is not None:
            cv_step_size = cast(int, cv_step_size)
        return cast(List[int], lags), cast(int, window_size), cast(int, max_horizon), \
            n_cross_validations, cv_step_size
    # Estimate heuristics if needed.
    if max_horizon == TimeSeries.AUTO:
        max_horizon = get_heuristic_max_horizon(
            X,
            automl_settings.time_column_name,
            automl_settings.grain_column_names)
    if window_size == TimeSeries.AUTO or lags == [TimeSeries.AUTO]:
        X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
        heuristics_lags, heuristics_rw = analyze_pacf_per_grain(
            X,
            automl_settings.time_column_name,
            TimeSeriesInternal.DUMMY_TARGET_COLUMN,
            automl_settings.grain_column_names)
        # Make sure we have removed the y back from the data frame.
        X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
        if window_size == TimeSeries.AUTO:
            window_size = heuristics_rw
        if lags == [TimeSeries.AUTO]:
            lags = [heuristics_lags]

    # short_series_handling_config should be an attribute and synced in the intialization of automl_base_settings.
    # If automl_base_settings doesn't have this attribute, it could have been manually deleted to test the legacy
    # mechanism.
    if not hasattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING_CONFIG):
        short_series_handling_config = \
            "drop" if getattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING, True) else None
    else:
        short_series_handling_config = getattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING_CONFIG)
    # CV is not enabled if n_cross_validations is None and no need for auto CV.
    if isinstance(lags, int):
        lags_list = [lags]
    else:
        lags_list = lags
    if n_cross_validations is not None:
        if n_cross_validations == TimeSeries.AUTO or cv_step_size == TimeSeries.AUTO:
            X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            n_cross_validations, cv_step_size = auto_cv_per_series(
                X,
                automl_settings.time_column_name,
                TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                cast(int, max_horizon),
                cast(List[int], lags_list),
                cast(int, window_size),
                n_cross_validations,
                cast(Union[str, int], cv_step_size),
                short_series_handling_config,
                automl_settings.grain_column_names)
            X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
        n_cross_validations = cast(int, n_cross_validations)
    if cv_step_size is not None:
        cv_step_size = cast(int, cv_step_size)

    return cast(List[int], lags), cast(int, window_size), cast(int, max_horizon), \
        n_cross_validations, cv_step_size
