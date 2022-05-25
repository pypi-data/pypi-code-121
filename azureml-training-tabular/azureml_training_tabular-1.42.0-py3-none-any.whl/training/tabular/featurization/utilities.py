# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for text featurization."""
import json
import logging
import re
import warnings
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import pandas.api as api

from .. import _constants as constants
from .._constants import DatetimeDtype, LanguageUnicodeRanges, NumericalDtype
from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import InvalidArgumentType
from .._diagnostics.validation import Validation
from .._types import CoreDataSingleColumnInputType

logger = logging.getLogger(__name__)

max_ngram_len = 3
# Regular expressions for date time detection
date_regex1 = re.compile(r"(\d+/\d+/\d+)")
date_regex2 = re.compile(r"(\d+-\d+-\d+)")


def get_ngram_len(lens_series):
    """
    Get N-grams length required for text transforms.

    :param lens_series: Series of lengths for a string.
    :return: The ngram to use.
    """
    if lens_series.shape[0] < 1:
        return 0

    lens_series = lens_series.apply(lambda x: min(x, max_ngram_len))
    return max(lens_series)


def wrap_in_list(x):
    return [x]


def _check_if_column_data_type_is_numerical(data_type_as_string: str) -> bool:
    """
    Check if column data type is numerical.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'integer', 'floating', 'mixed-integer-float' or 'decimal'.
                     'False' otherwise.

    """
    if data_type_as_string in list(NumericalDtype.FULL_SET):
        return True

    return False


def _check_if_column_data_type_is_datetime(data_type_as_string: str) -> bool:
    """
    Check if column data type is datetime.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'date', 'datetime' or 'datetime64'. 'False' otherwise.

    """
    return data_type_as_string in DatetimeDtype.FULL_SET


def _check_if_column_data_type_is_int(data_type_as_string: str) -> bool:
    """
    Check if column data type is integer.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        boolean -- 'True' if the dtype returned is 'integer'. 'False' otherwise.

    """
    if data_type_as_string == NumericalDtype.Integer:
        return True

    return False


def _check_if_column_data_is_nonspaced_language(unicode_median_value: int) -> bool:
    """
    Check if the median of unicode value belongs to a nonspaced language.

    Arguments:
        unicode_median_value {int} -- median of unicode values of the entire column.

    Returns:
        boolean -- 'True' if the unicode median value is within the unicode ranges of
        languages that has no spaces and supported by bert multilingual.
                        'False' otherwise.

    """
    for range_ in LanguageUnicodeRanges.nonspaced_language_unicode_ranges:
        if range_[0] <= unicode_median_value <= range_[1]:
            return True

    return False


def get_value_int(intstring: str) -> Optional[Union[int, str]]:
    """
    Convert string value to int.

    :param intstring: The input value to be converted.
    :type intstring: str
    :return: The converted value.
    :rtype: int
    """
    if intstring is not None and intstring != "":
        return int(intstring)
    return intstring


def get_value_float(floatstring: str) -> Optional[Union[float, str]]:
    """
    Convert string value to float.
    :param floatstring: The input value to be converted.
    :type floatstring: str
    :return: The converted value.
    :rtype: float
    """
    if floatstring is not None and floatstring != "":
        return float(floatstring)
    return floatstring


def get_value_from_dict(dictionary: Dict[str, Any], names: List[str], default_value: Any) -> Any:
    """
    Get the value of a configuration item that has a list of names.

    :param dictionary: Dictionary of settings with key value pair to look the data for.
    :type dictionary: dict
    :param names: The list of names for the item looking foi.
    :type names: list[str]
    :param default_value: Default value to return if no matching key found
    :return: Returns the first value from the list of names.
    """
    for key in names:
        if key in dictionary:
            return dictionary[key]
    return default_value


def subsampling_recommended(num_samples):
    """

    :param num_samples: number of samples.
    :type num_samples: int
    :return: True if subsampling is recommended, else False.
    :rtype: bool
    """
    return num_samples >= 50000


def _log_raw_data_stat(raw_feature_stats, prefix_message=None):
    if prefix_message is None:
        prefix_message = ""
    raw_feature_stats_dict = dict()
    for name, stats in raw_feature_stats.__dict__.items():
        try:
            stats_json_str = json.dumps(stats)
        except (ValueError, TypeError):
            stats_json_str = json.dumps(dict())
        raw_feature_stats_dict[name] = stats_json_str
    logger.info("{}RawFeatureStats:{}".format(prefix_message, json.dumps(raw_feature_stats_dict)))


def _get_ts_params_dict(automl_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get time series parameter data.

    Arguments:
        automl_settings {AutoMLSettings} -- automl settings object

    Returns:
        dict -- a dictionary of time series data info

    """
    if automl_settings.is_timeseries:
        dict_time_series = {
            constants.TimeSeries.TIME_COLUMN_NAME: automl_settings.time_column_name,
            constants.TimeSeries.GRAIN_COLUMN_NAMES: automl_settings.grain_column_names,
            constants.TimeSeries.DROP_COLUMN_NAMES: automl_settings.drop_column_names,
            constants.TimeSeriesInternal.OVERWRITE_COLUMNS: automl_settings.overwrite_columns,
            constants.TimeSeriesInternal.DROP_NA: automl_settings.dropna,
            constants.TimeSeriesInternal.TRANSFORM_DICT: automl_settings.transform_dictionary,
            constants.TimeSeries.MAX_HORIZON: automl_settings.max_horizon,
            constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME:
                constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT,
            constants.TimeSeries.COUNTRY_OR_REGION: automl_settings.country_or_region,
            constants.TimeSeriesInternal.CROSS_VALIDATIONS: automl_settings.n_cross_validations,
            constants.TimeSeries.SHORT_SERIES_HANDLING: automl_settings.short_series_handling,
            constants.TimeSeries.MAX_CORES_PER_ITERATION: automl_settings.max_cores_per_iteration,
            constants.TimeSeries.FEATURE_LAGS: automl_settings.feature_lags,
            constants.TimeSeries.TARGET_AGG_FUN: automl_settings.target_aggregation_function,
            constants.TimeSeries.CV_STEP_SIZE: automl_settings.cv_step_size,
        }
        # Set window size and lags only if user did not switched it off by setting to None.
        if automl_settings.window_size is not None:
            dict_time_series[constants.TimeSeriesInternal.WINDOW_SIZE] = automl_settings.window_size
        if automl_settings.lags is not None:
            dict_time_series[constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT] = automl_settings.lags
        if automl_settings.iteration_timeout_minutes is not None:
            dict_time_series[
                constants.TimeSeries.ITERATION_TIMEOUT_MINUTES
            ] = automl_settings.iteration_timeout_minutes
        if hasattr(automl_settings, constants.TimeSeries.SEASONALITY):
            dict_time_series[constants.TimeSeries.SEASONALITY] = getattr(
                automl_settings, constants.TimeSeries.SEASONALITY
            )
        if hasattr(automl_settings, constants.TimeSeries.USE_STL):
            dict_time_series[constants.TimeSeries.USE_STL] = getattr(automl_settings, constants.TimeSeries.USE_STL)
        if hasattr(automl_settings, constants.TimeSeries.FREQUENCY):
            dict_time_series[constants.TimeSeries.FREQUENCY] = getattr(automl_settings, constants.TimeSeries.FREQUENCY)
        if hasattr(automl_settings, constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG):
            dict_time_series[constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG] = getattr(
                automl_settings, constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG
            )
        return dict_time_series
    else:
        return None


def _get_gpu_training_params_dict(automl_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get gpu training related parameter data.

    Arguments:
        automl_settings {AutoMLSettings} -- automl settings object

    Returns:
        dict -- a dictionary of gpu training info

    """
    if hasattr(automl_settings, "is_gpu") and automl_settings.is_gpu:
        dict_gpu_training = {"processing_unit_type": "gpu"}
        return dict_gpu_training
    else:
        return None


def convert_dict_values_to_str(input_dict: Dict[Any, Any]) -> Dict[str, str]:
    """
    Convert a dictionary's values so that every value is a string.

    :param input_dict: the dictionary that should be converted
    :return: a dictionary with all values converted to strings
    """
    fit_output_str = {}
    for key in input_dict:
        if input_dict[key] is None:
            fit_output_str[str(key)] = ""
        else:
            # Cast to string to avoid warnings (PR 143137)
            fit_output_str[str(key)] = str(input_dict[key])
    return fit_output_str


def to_ordinal_string(integer: int) -> str:
    """
    Convert an integer to an ordinal string.

    :param integer:
    :return:
    """
    return "%d%s" % (integer, "tsnrhtdd"[(integer / 10 % 10 != 1) * (integer % 10 < 4) * integer % 10 :: 4])


def is_known_date_time_format(datetime_str: str) -> bool:
    """
    Check if a given string matches the known date time regular expressions.

    :param datetime_str: Input string to check if it's a date or not
    :return: Whether the given string is in a known date time format or not
    """
    if date_regex1.search(datetime_str) is None and date_regex2.search(datetime_str) is None:
        return False

    return True


def _to_str_recursive(value: Any) -> Any:
    """
    Convert the value to JSON serializable form.

    :param value: The value to be converted to the JSON-serializable form.
    :return: the value in the python serializable form.
    """
    if isinstance(value, list):
        return [_to_str_recursive(val) for val in value]
    elif isinstance(value, tuple):
        return tuple(_to_str_recursive(val) for val in value)
    elif isinstance(value, dict):
        # We convert key to string, because otherwise it will not be JSON
        # serializable.
        return {str(k): _to_str_recursive(v) for k, v in value.items()}
    else:
        return str(value)


def get_min_points(
    window_size: int, lags: List[int], max_horizon: int, cv: Optional[int], n_step: Optional[int] = None
) -> int:
    """
    Return the minimum number of data points needed for training.

    :param window_size: the rolling window size.
    :param lags: The lag size.
    :param max_horizon: the desired length of forecasting.
    :param cv: the number of cross validations.
    :param n_step:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :return: the minimum number of data points.
    """
    min_points = max_horizon + max(window_size, max(lags)) + 1
    if n_step is None:
        n_step = 1
    if cv is not None:
        min_points = min_points + (cv - 1) * n_step + 1 + max_horizon
    return min_points


def _get_column_data_type_as_str(array: CoreDataSingleColumnInputType) -> str:
    """
    Infer data type of the input array.

    :param array: input column array to detect type
    :raise ValueError if array is not supported type or not valid
    :return: type of column as a string (integer, floating, string etc.)
    """
    # If the array is not valid, then throw exception
    Validation.validate_value(array, "array")

    # If the array is not an instance of ndarray, then throw exception
    if (
        not isinstance(array, np.ndarray)
        and not isinstance(array, pd.Series)
        and not isinstance(array, pd.Categorical)
        and not isinstance(array, pd.core.arrays.sparse.SparseArray)
        and not isinstance(array, pd.core.arrays.integer.IntegerArray)
    ):
        raise AzureMLError.create(
            InvalidArgumentType,
            argument="array",
            actual_type=type(array),
            expected_types="numpy.ndarray, pandas.Series, pandas.Categorical,\
                pandas.core.arrays.sparse.SparseArray, pandas.core.arrays.integer.IntegerArray",
        )

    # Ignore the Nans and then return the data type of the column
    return str(api.types.infer_dtype(array, skipna=True))


def _get_unique(col: CoreDataSingleColumnInputType) -> Any:
    """
    Get pandas Series containing unique values.

    :param col: DataSingleColumnInputType
    :return: unique values of the given input column.
    """
    try:
        return np.sort(pd.unique(col))
    except TypeError:
        # TypeError Thrown when column includes unhashable type. Try again after converting them to string.
        # Example error msg:
        # TypeError: unhashable type: 'list', thrown for pd.unique(col)
        warnings.warn(
            "The input data has mixed data types, to procceed we will convert it to STRING type, "
            "expect the trained model to predict values in STRING type. "
            "Otherwise please consider cleaning up."
        )
        return np.sort(pd.unique([str(i) for i in col]))


def _get_num_unique(col: CoreDataSingleColumnInputType, ignore_na: bool = False) -> Any:
    """
    Get number of unique values in the given column.

    :param col: DataSingleColumnInputType
    :return: distinct count of the column.
    """
    if ignore_na:
        non_na_col = col[~pd.isna(col)]
        return _get_unique(non_na_col).shape[0]

    return _get_unique(col).shape[0]
