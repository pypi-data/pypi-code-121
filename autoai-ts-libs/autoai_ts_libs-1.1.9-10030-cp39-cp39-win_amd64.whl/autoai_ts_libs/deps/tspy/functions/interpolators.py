"""
main entry point for time-series interpolators
"""

#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/
from autoai_ts_libs.deps.tspy import _get_context

def linear(fill_value=None, history_size=1, future_size=1):
    """fill null value with the value derived using linear interpolation (using a few values in the left and a few values in the right)"""
    tsc = _get_context()
    if fill_value is not None:
        fill_value = tsc.java_bridge.cast_to_j_if_necessary(fill_value)
    return tsc.packages.time_series.transforms.interpolators.Interpolators.linear(fill_value, history_size,
                                                                                              future_size)


def cubic(fill_value=None, history_size=3, future_size=3):
    """fill null value with the value derived using cubic interpolation (using a few values in the left and a few values in the right)"""
    tsc = _get_context()
    if fill_value is not None:
        fill_value = tsc.java_bridge.cast_to_j_if_necessary(fill_value)
    return tsc.packages.time_series.transforms.interpolators.Interpolators.cubic(fill_value, history_size,
                                                                                             future_size)


def next(default_value=None):
    """fill null value with the next value, and if there is none, get `default_value`"""
    tsc = _get_context()
    if default_value is not None:
        default_value = tsc.java_bridge.cast_to_j_if_necessary(default_value)
    return tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.next(default_value)


def prev(default_value=None):
    """fill null value with the previous value, and if there is none, get `default_value`"""
    tsc = _get_context()
    if default_value is not None:
        default_value = tsc.java_bridge.cast_to_j_if_necessary(default_value)
    return tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.prev(default_value)


def nearest(default_value=None):
    """fill null value with the nearest value, and if there is none, get `default_value`"""
    tsc = _get_context()
    if default_value is not None:
        default_value = tsc.java_bridge.cast_to_j_if_necessary(default_value)
    return tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nearest(default_value)


def fill(value):
    """fill null value with the given `value`"""
    tsc = _get_context()
    if value is not None:
        value = tsc.java_bridge.cast_to_j_if_necessary(value)
    return tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.fill(value)


def nullify():
    """set the given data to null value"""
    tsc = _get_context()
    return tsc.packages.time_series.core.core_transforms.general.GenericInterpolators.nullify()
