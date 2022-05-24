#!/usr/bin/env python3
# coding: utf-8

"""
This module is deprecated.
This module will be removed in version 0.6.0.
"""

import warnings
from joker.redis.loggers import RedisHandler, ErrorInterface

warnings.warn(
    "joker.flasky.loggers is deprecated. Use joker.redis.loggers instead.",
    DeprecationWarning,
)

_compat = [
    RedisHandler,
    ErrorInterface,
]

__all__ = []
