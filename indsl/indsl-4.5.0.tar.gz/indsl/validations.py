from typing import Union

import pandas as pd

from .exceptions import UserTypeError, UserValueError


def validate_series_has_time_index(data: pd.Series):
    """Helper method to validate if provided pandas.Series is of type pandas.DatetimeIndex"""
    if not isinstance(data.index, pd.DatetimeIndex):
        raise UserTypeError(f"Expected a time series, got index type {data.index.dtype}")


def validate_series_is_not_empty(series: Union[pd.Series, pd.DataFrame]):
    if len(series) == 0:
        raise UserValueError("Time series is empty.")


def validate_series_has_minimum_length(series: pd.Series, min_len: int):
    if len(series) < min_len:
        raise UserValueError(f"Expected series with length >= {min_len}, got length {len(series)}")


def validate_timedelta_unit(timedelta: pd.Timedelta):
    if timedelta < pd.Timedelta(seconds=1):
        raise UserValueError("Unit of timedelta should be in days, hours, minutes or seconds")
