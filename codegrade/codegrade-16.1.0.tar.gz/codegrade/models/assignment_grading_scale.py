"""This module defines the enum AssignmentGradingScale.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentGradingScale(str, Enum):
    points = "points"
    percentage = "percentage"
