"""This module defines the enum AssignmentKind.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentKind(str, Enum):
    normal = "normal"
    exam = "exam"
