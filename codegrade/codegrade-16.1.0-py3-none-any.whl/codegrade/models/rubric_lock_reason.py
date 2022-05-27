"""This module defines the enum RubricLockReason.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class RubricLockReason(str, Enum):
    auto_test = "auto_test"
