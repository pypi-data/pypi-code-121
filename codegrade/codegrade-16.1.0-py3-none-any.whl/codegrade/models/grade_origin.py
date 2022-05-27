"""This module defines the enum GradeOrigin.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class GradeOrigin(str, Enum):
    human = "human"
    auto_test = "auto_test"
    rubric_migration = "rubric_migration"
