"""This module defines the enum AssignmentExportColumn.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentExportColumn(str, Enum):
    id = "id"
    username = "username"
    name = "name"
    grade = "grade"
    created_at = "created_at"
    assigned_to = "assigned_to"
    general_feedback = "general_feedback"
    line_feedback = "line_feedback"
