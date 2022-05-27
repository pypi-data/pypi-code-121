"""This module defines the enum IOTestOption.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class IOTestOption(str, Enum):
    case = "case"
    trailing_whitespace = "trailing_whitespace"
    substring = "substring"
    regex = "regex"
    all_whitespace = "all_whitespace"
