"""This module defines the enum CourseState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class CourseState(str, Enum):
    visible = "visible"
    archived = "archived"
    deleted = "deleted"
