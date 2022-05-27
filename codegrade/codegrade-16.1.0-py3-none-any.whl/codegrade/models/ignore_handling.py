"""This module defines the enum IgnoreHandling.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class IgnoreHandling(str, Enum):
    keep = "keep"
    delete = "delete"
    error = "error"
