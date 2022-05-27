"""This module defines the enum DeletionType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class DeletionType(str, Enum):
    empty_directory = "empty_directory"
    denied_file = "denied_file"
    leading_directory = "leading_directory"
