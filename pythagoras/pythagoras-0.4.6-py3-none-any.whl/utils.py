"""Miscellaneous supporting classes and functions."""

from __future__ import annotations

from abc import ABCMeta
import datetime
import math
import os
import platform
import socket
from getpass import getuser
import inspect
import numbers, time
from typing import Any, Dict
import pkg_resources
import psutil
import gc
import string


def get_safe_chars():
    """ Get set of URL/filename-safe characters.

     A set of characters allowed in Persistent Dict keys,
     filenames / S3 object names, and hash addresses.
     """
    chars = set(string.ascii_letters + string.digits + "()_-~.=")
    return chars


def replace_unsafe_chars(a_str:str, replace_with:str) -> str :
    """ Replace unsafe (special) characters with allowed (safe) ones."""
    safe_chars = get_safe_chars()
    result_list = [(c if c in safe_chars else replace_with) for c in a_str]
    result_str = "".join(result_list)
    return result_str


class ABC_PostInitializable(ABCMeta):
    """ Metaclass that enables __post__init__() method for abstract classes. """
    def __call__(cls, *args, **kwargs):
        obj = ABCMeta.__call__(cls, *args, **kwargs)
        obj.__post__init__(*args, **kwargs)
        return obj


def buid_context(file_path:str=None, time_zone=None)-> Dict:
    """Capture core information about execution environment. """

    result = dict(
        date_time = datetime.datetime.now(time_zone)
        ,hostname = socket.gethostname()
        ,user = getuser()
        ,pid = os.getpid()
        ,platform = platform.platform()
        ,python_implementation = platform.python_implementation()
        ,python_version = platform.python_version()
        ,processor = platform.processor()
        ,cpu_count = psutil.cpu_count()
        ,cpu_load_avg = psutil.getloadavg()
        ,disk_usage = psutil.disk_usage(file_path)
        ,virtual_memory = psutil.virtual_memory()
        ,available_packages = pkg_resources.working_set
        )

    return result


def get_long_infoname(x:Any, drop_unsafe_chars:bool = True) -> str:
    """Build a string with extended information about an object and its type"""

    name = str(type(x).__module__)

    if hasattr(type(x), "__qualname__"):
        name += "." + str(type(x).__qualname__)
    else:
        name += "." + str(type(x).__name__)

    if hasattr(x, "__qualname__"):
        name += "___" + str(x.__qualname__)
    elif hasattr(x, "__name__"):
        name += "___" + str(x.__name__)

    if drop_unsafe_chars:
        name = replace_unsafe_chars(name, "_")

    return name


class NeatStr:
    """Nice short human-readable str depictions of popular numeric values.

    Insignificant details are dropped:
    - exact # of seconds is not shown if we are talking about hours,
    - exact # of bytes is dropped if we are talking about gigabytes, etc.
    """

    @staticmethod
    def mem_size(size_in_B:int, div_ch:str = ' ') -> str:
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
    """ Force garbage collection and return/print size of fee memory. """

    if collect_garbage:
        gc.collect()

    free_memory = psutil.virtual_memory().free

    if print_info:
        print(f"Free memory: {NeatStr.mem_size(free_memory)} ")

    return free_memory


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