# -*- coding:utf-8 -*-
from __future__ import absolute_import

import cProfile
import logging
import pstats
import time

import functools
import re


class TimeCostHelper(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._time_start = time.time()
        self._last_time = time.time()

    def dot(self, info_format: str = None):
        now = time.time()
        time_cost_seconds = now - self._last_time
        self._last_time = now
        if info_format:
            self.logger.info(info_format.format(time_cost_seconds))
        else:
            self.logger.info("Time cost {}s".format(time_cost_seconds))

    def sum(self, info_format: str = None):
        now = time.time()
        time_cost_seconds = now - self._time_start
        if info_format:
            self.logger.info(info_format.format(time_cost_seconds))
        else:
            self.logger.info("Total time cost {}s".format(time_cost_seconds))


def time_cost(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info("<{}> cost time: {}s".format(func.__name__, time.time() - start_time))
        return result

    return wrapper


def c_profile_demo():
    print(re)  # re must import
    cProfile.run('re.compile("foo|bar")')


def do_c_profile(prof_file: str):
    """
    ref: https://zhuanlan.zhihu.com/p/24495603
    Decorator for function profiling.
    """

    def wrapper(func):
        def profiled_func(*args, **kwargs):
            # Flag for do profiling or not.
            profile = cProfile.Profile()
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            # Sort stat by internal time.
            sort_by = "tottime"
            ps = pstats.Stats(profile).sort_stats(sort_by)
            ps.dump_stats(prof_file)
            return result

        return profiled_func

    return wrapper


def parse_c_profile_file(prof_file: str):
    p = pstats.Stats(prof_file)
    p.strip_dirs().sort_stats("cumtime").print_stats(10, 1.0, ".*")


__all__ = ("time_cost", "do_c_profile", "parse_c_profile_file", "TimeCostHelper")
