# from __future__ import annotations
# Above is temporarily commented to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation

import logging as lg
import math
import numpy as np
import inspect
import numbers, time
from typing import Any, ClassVar, Union
from copy import deepcopy
import psutil
import gc
# import logging
# import pandas as pd

from scipy import stats
from sklearn.base import BaseEstimator
from sklearn.datasets import load_boston, fetch_california_housing

def update_param_if_supported(
        estimator: BaseEstimator
        ,param_name:str
        ,param_value:Any
        ) -> BaseEstimator:
    current_params = estimator.get_params()
    if param_name in current_params:
        new_params = {**current_params, param_name:param_value}
        return type(estimator)(**new_params)
    return type(estimator)(**current_params)


class TempAttributeAssignmentIfNotNone:
    """Context manager that temporarily changes a value of an object attribute

    This class is designed to be used with a "with" statement, and it allows
    to temporarily change an attribute of an object to a new value,
    provided that the new value is not None.
    """
    def __init__(self, an_object:Any, attr_name:str, tmp_value:Any):
        assert hasattr(an_object,attr_name), (
            f"Object {NeatStr.object_info(an_object)} is required"
            + f" to have an attribute {attr_name}")
        self.an_object = an_object
        self.attr_name = attr_name
        self.tmp_value = tmp_value

    def __enter__(self):
        if self.tmp_value is not None:
            self.old_value = getattr(self.an_object, self.attr_name)
            setattr(self.an_object, self.attr_name, self.tmp_value)

    def __exit__(self, *args, **kwargs):
        if self.tmp_value is not None:
            setattr(self.an_object, self.attr_name, self.old_value)


class NeatStr:
    """Nice short human-readable str depictions of popular numeric values.

    Insignificant details are dropped:
    - exact # of seconds is not shown if we are talking about hours,
    - exact # of bytes is dropped if we are talking about gigabytes, etc.
    """

    @staticmethod
    def mem_size(size_in_B: int, div_ch: str = ' ') -> str:
        """Convert an integer number of bytes into a string like '7 Mb' """
        assert isinstance(size_in_B, numbers.Number)
        assert size_in_B >= 0

        size_in_K = size_in_B / 1024
        if size_in_K < 1: return (str(math.ceil(size_in_B))) + div_ch + "B"

        size_in_M = size_in_K / 1024
        if size_in_M < 1: return (str(math.ceil(size_in_K))) + div_ch + "Kb"

        size_in_G = size_in_M / 1024
        if size_in_G < 1: return (str(math.ceil(size_in_M))) + div_ch + "Mb"

        size_in_T = size_in_G / 1024
        if size_in_T < 1: return (str(math.ceil(size_in_G))) + div_ch + "Gb"

        size_in_P = size_in_T / 1024
        if size_in_P < 1: return (str(math.ceil(size_in_T))) + div_ch + "Tb"

        return (str(math.ceil(size_in_P))) + div_ch + "Pb"

    @staticmethod
    def time_diff(time_in_seconds: float, div_ch: str = ' ') -> str:
        """Convert a float number of seconds into a string like '5 hours' """
        t = time_in_seconds
        t_str = ""

        h = t / (60 * 60)
        if h >= 1:
            t_str += str(math.floor(h)) + div_ch + "hours" + div_ch
            t = t - h * (60 * 60)

        m = t / 60
        if m >= 1:
            t_str += str(math.floor(m)) + div_ch + "minutes" + div_ch
            t = t - m * 60

        if h < 1:
            if m > 1:
                t_str += str(math.ceil(t))
            elif t >= 10:
                t_str += f"{t:.1f}"
            elif t >= 1:
                t_str += f"{t:.2f}"
            else:
                t_str += f"{t:.3g}"

            t_str += div_ch + "seconds" + div_ch

        t_str = t_str.rstrip(div_ch)
        return t_str

    @staticmethod
    def object_names(
            an_object: Any
            , div_ch: str = '.'
            , stacks_to_skip:int = 0) -> str:
        """ Find the name(s) of variable(s) that are aliases for an_object.

        The function uses a naive but fast approach,
        it does not always find all the names
        """
        all_names = []

        for f in reversed(inspect.stack()[stacks_to_skip+1:]):
            local_vars = f.frame.f_locals
            names = [name for name in local_vars if
                     local_vars[name] is an_object]
            if "self" in names:
                names.remove("self")
            all_names += names

        all_names = list(dict.fromkeys(all_names))  # dedup but keep the order

        return div_ch.join(all_names)

    @staticmethod
    def object_info(
            an_object: Any
            , div_ch: str = '.'
            , stacks_to_skip: int = 0) -> str:
        """ Create a string with debug information about an object"""

        names_str = NeatStr.object_names(
            an_object, div_ch=" / ",stacks_to_skip = stacks_to_skip+1)

        if names_str.count("/"):
            text_info = "An object with names < " + names_str + " >"
        elif len(names_str):
            text_info = "An object with name < " + names_str + " >"
        else:
            text_info = "An anonymous object"

        text_info += " has type < "
        if hasattr(type(an_object),"__qualname__"):
            text_info += type(an_object).__qualname__
        else:
            text_info += type(an_object).__name__
        text_info += " > and repr_value < "
        text_info += repr(an_object)
        text_info += " >"

        text_info = text_info.replace("  ", " ")
        text_info = text_info.replace("< <", "< ")
        text_info = text_info.replace("> >", " >")

        return text_info

def free_RAM(print_info:bool=True, collect_garbage:bool=True) -> int:
    if collect_garbage:
        gc.collect()

    free_memory = psutil.virtual_memory().free

    if print_info:
        print(f"Free memory: {NeatStr.mem_size(free_memory)} ")

    return free_memory

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class BasicStopwatch:
    pass

class BasicStopwatch:
    """Simple class to measure time durations."""

    start_time: float
    stop_time: float

    def __init__(self, start: bool = False) -> None:
        self.reset_timer(start)

    def reset_timer(self, start: bool = False) -> BasicStopwatch:
        if start:
            self.start_timer()
        else:
            self.start_time = 0
            self.stop_time = 0
        return self

    def start_timer(self) -> BasicStopwatch:
        self.start_time = time.time()
        self.stop_time = 0
        return self

    def stop_timer(self) -> BasicStopwatch:
        assert self.stop_time == 0
        self.stop_time = time.time()
        assert self.start_time != 0
        return self

    def get_float_repr(self) -> float:
        assert self.stop_time != 0
        return self.stop_time - self.start_time

    def __str__(self) -> str:
        return NeatStr.time_diff(self.get_float_repr())

#
# class AssertableObject:
#     """An abstract base class for types that offer run-time sanity checks."""
#
#     EXTRA_SAFETY_FLAG:ClassVar[bool] = True
#
#     def __init__(self) -> None:
#         assert type(self) != AssertableObject, (
#             f"Class {type(self).__name__} can not be instantiated.")
#         self.assert_sanity()
#
#     # V-V-V-V-V-V-V-V-V-V-V---Virtual-Method---V-V-V-V-V-V-V-V-V-V-V-V-V-V-V
#     def assert_sanity(self) -> None:
#         """Check self for structural consistency; halt if there are errors"""
#         raise NotImplementedError


##########################################
# 1-argument aggregators

def percentile01(data):
    return np.nanpercentile(data, 1)


def percentile05(data):
    return np.nanpercentile(data, 5)


def percentile10(data):
    return np.nanpercentile(data, 10)


def percentile20(data):
    return np.nanpercentile(data, 20)


def percentile25(data):
    return np.nanpercentile(data, 25)


def percentile30(data):
    return np.nanpercentile(data, 30)


def percentile40(data):
    return np.nanpercentile(data, 40)


def percentile50(data):
    return np.nanpercentile(data, 50)


def percentile60(data):
    return np.nanpercentile(data, 60)


def percentile70(data):
    return np.nanpercentile(data, 70)


def percentile75(data):
    return np.nanpercentile(data, 75)


def percentile80(data):
    return np.nanpercentile(data, 80)


def percentile90(data):
    return np.nanpercentile(data, 90)


def percentile95(data):
    return np.nanpercentile(data, 95)


def percentile99(data):
    return np.nanpercentile(data, 99)


def minmode(data):
    return min(stats.mode(data, nan_policy="omit")[0])


def maxmode(data):
    return -min(stats.mode(-data, nan_policy="omit")[0])

def root_2(x):
    return x**0.5

def power_2(x):
    return x*x

def power_3(x):
    return x*x*x

def passthrough(x):
    return deepcopy(x)

def power_m1_1p(x):
    return 1/(x+1)
