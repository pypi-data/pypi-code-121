#!/usr/bin/env python3
# coding: utf-8

"""
Deprecated. This module will be removed on ver 0.6.0.
"""

import warnings
from joker.flasky.auth import HashedPassword


warnings.warn(
    "joker.flasky.security is deprecated. Use joker.flasky.auth instead.",
    DeprecationWarning,
)

__all__ = []
__deprecated__ = [HashedPassword]
