# coding=utf-8
from __future__ import absolute_import, print_function

import functools
import itertools
import time

from suanpan import utils
from suanpan.log import logger


def formatFuncCall(func, *args, **kwargs):
    paramString = ", ".join(
        itertools.chain((str(a) for a in args), (f"{k}={v}" for k, v in kwargs.items()))
    )
    funcString = f"{func.__name__}({utils.shorten(paramString)})"
    return funcString


def costCall(func, *args, **kwargs):
    startTime = time.time()
    result = func(*args, **kwargs)
    endTime = time.time()
    costTime = endTime - startTime
    return costTime, result


def print(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(f"{formatFuncCall(func, *args, **kwargs)} - {result}")
        return result

    return _dec
