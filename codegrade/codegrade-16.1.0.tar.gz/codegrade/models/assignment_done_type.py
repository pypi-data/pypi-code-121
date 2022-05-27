"""This module defines the enum AssignmentDoneType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentDoneType(str, Enum):
    assigned_only = "assigned_only"
    all_graders = "all_graders"
