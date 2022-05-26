# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 15:39:47 2021

@author: jvorsten
"""

# Python imports
from typing import List, Iterable
from datetime import datetime
from copy import deepcopy
import math

# Thrid party imports
import numpy as np
import pandas as pd

# Local imports
from .FDDExceptions import FDDException

# %%


def read_csv(filepath, headers, dtypes):
    """Wrapper for pandas read_csv method. Read a CSV file into a dataframe
    object with the specified types for dual-duct VAV units.
    This method enforces datatypes and headers for the input CSV file
    format"""
    df = pd.read_csv(filepath, sep=',', usecols=headers,
                     parse_dates=['DateTime'], dtype=dtypes)
    return df


def _parse_date_time_str_YmdHM(dates: Iterable[str], times: Iterable[str]) -> List[datetime]:
    """Parse incomplete ISO times in the format H:MM:SS to HH:MM:SS as a 
    python time datetime.time object
    inputs
    -------
    dates: (list) of strings representing date in format %Y-%m-%d
    times: (list) of strings representing time in format %H:%M"""
    iso_times = []
    for date_str, time_str in zip(dates, times):
        iso_times.append(datetime.strptime(
            date_str + time_str, "%Y-%m-%d%H:%M"))

    return iso_times


def _correct_time_str_HM(times: Iterable[str]) -> List[str]:
    """Parse incomplete ISO times in the format H:MM to HH:MM as a 
    python time datetime.time object"""
    iso_times = []
    for time_str in times:
        if len(time_str) == 4:
            iso_times.append("0" + time_str)
        else:
            iso_times.append(time_str)

    return iso_times


def masked_consecutive_elements(data: np.ma.MaskedArray, n_consecutive_elements: int) -> List[int]:
    """Return indices where a masked array is True for n_consecutive_elements
    for rising edge only
    inputs
    -------
    data: (np.ma.MaskedArray) array of 0,1 representing a test condition. This
    function reports consecutive 1s
    output
    -------
    rising_edge: list[int] of indices where there are consecutive elements
    example
    data = np.ma.MaskedArray([0,0,0,0,1,1,1,0,0,0,1,1,1])
    res = masked_consecutive_elements(data, 3) # [4, 10]
    >>> res
    out: [4, 10]
    """
    rising_edge = []
    pushed = False
    consecutive_count = 0

    for i in range(0, data.shape[0]):
        if data[i]:
            consecutive_count += 1
            if consecutive_count == n_consecutive_elements and not pushed:
                rising_edge.append(i - n_consecutive_elements + 1)
                pushed = True
        else:
            consecutive_count = 0
            pushed = False

    return rising_edge


def masked_rolling_sum(data: np.ma.MaskedArray, n_consecutive_elements: int):
    """Return the indices of a masked array that contain 'n' consecutive 
    True elements"""
    window_sum = np.zeros((data.shape[0] - n_consecutive_elements))
    for i in range(0, data.shape[0] - n_consecutive_elements):
        window_sum[i] = np.sum(data[i:n_consecutive_elements])

    return np.where(window_sum == n_consecutive_elements)


def _datetimes_to_seconds_deviation_from_start(datetimes: Iterable[datetime]) -> np.array:
    """Given an iterable of datetime objects, return an equally sized numpy
    array where each element in the array is the number of seconds deviation 
    from the first element in the datetime iterable
    Assumes all datetimes are ascending order
    inputs
    -------
    datetime: (iterable) of datetime / pd.DateTime"""

    time_delta = np.empty((len(datetimes)))
    for i in range(0, len(time_delta)):
        time_delta[i] = (datetimes[i] - datetimes[0]).seconds

    return time_delta


def _hour_segment_indices_from_seconds(seconds: Iterable[int]) -> List[List[int]]:
    """Given an iterable of datetime elements, yield sequential list of indices
    that fall within a hour window
    inputs
    ------
    datetimes: (iterable) of integers representing seconds
    Example
    seconds = [0,900,2700,4500,8100] # [0,5,45,75,135] minutes
    res = _hour_segment_indices_from_seconds(seconds)
    >>> res # [[0,1,2],[3],[4]]
    """
    previous_hour = 0
    indices = []
    segment = []

    for i in range(0, len(seconds)):
        if seconds[i] - seconds[previous_hour] >= 3600:
            indices.append(deepcopy(segment))
            segment.clear()
            segment.append(i)
            previous_hour = i
        else:
            segment.append(i)

    if len(indices) == 0:
        # nothing got appended to indices
        indices.append(segment)

    # Handle the last element
    try:
        last_element = indices[-1][-1]
    except IndexError:
        indices[-1].append(i)
        return indices

    if last_element == len(seconds):
        # The last time segment was exactly an hour
        return indices
    else:
        # The last time segment was not a full hour
        indices[-1].append(i)

    return indices


def maximum_allowed_failures(mask: np.ma.MaskedArray,
                             data: pd.DataFrame,
                             failure_percent: float,
                             report_columns: List[str],
                             error_msg: str) -> None:
    """Raise a FDDException if the maximum number of failures within a mask is 
    exceeded"""

    max_failures = math.floor(failure_percent * len(mask))
    if mask.sum() > max_failures:
        report_indices = mask.nonzero()[0][:max_failures]
        data_view = data.loc[report_indices,
                             report_columns].to_dict(orient='list')
        gmsg = ("The maximum allowed instances ({} at {:.0%} of samples) was " +
                "exceeded ({} observed)")
        msg = error_msg + "\n" + gmsg
        msg = msg.format(max_failures, failure_percent, mask.sum())
        data_view['primary_axis_label'] = report_columns[0]
        data_view['dependent_axis_labels'] = report_columns[1:]
        raise FDDException(msg, data_view)

    return None


def failure_threshold_exceeded(data: pd.DataFrame,
                               report_columns: List[str],
                               report_indices: List[int],
                               error_msg: str) -> None:
    """Raise a FDDException if the calculated threshold of failures is
    exceeded
    Useful for calculated thresholds (total sum, integration, etc.)"""

    data_view = data.loc[report_indices, report_columns].to_dict(orient='list')
    gmsg = ("Failure threshold exceeded")
    msg = error_msg + "\n" + gmsg
    data_view['primary_axis_label'] = report_columns[0]
    data_view['dependent_axis_labels'] = report_columns[1:]
    raise FDDException(msg, data_view)

    return None


def maximum_consecutive_failures(mask: np.ma.MaskedArray,
                                 data: pd.DataFrame,
                                 failure_consecutive: float,
                                 report_columns: List[str],
                                 error_msg: str) -> None:

    consecutive_indices = masked_consecutive_elements(
        mask, failure_consecutive)
    if len(consecutive_indices) > 0:
        report_indices = np.arange(max(0, consecutive_indices[0] - 10),
                                   min(consecutive_indices[0] +
                                       10, data.shape[0]),
                                   step=1, dtype=int)
        data_view = data.loc[report_indices,
                             report_columns].to_dict(orient='list')
        gmsg = ("The maximum allowed consecutive instances ({}) was exceeded " +
                "starting at data indices {}")
        msg = error_msg + "\n" + gmsg
        msg = msg.format(failure_consecutive, consecutive_indices)
        data_view['primary_axis_label'] = report_columns[0]
        data_view['dependent_axis_labels'] = report_columns[1:]
        raise FDDException(msg, data_view)

    return None
