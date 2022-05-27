"""This module defines the enum CGIgnoreVersion.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class CGIgnoreVersion(str, Enum):
    EmptySubmissionFilter = "EmptySubmissionFilter"
    IgnoreFilterManager = "IgnoreFilterManager"
    SubmissionValidator = "SubmissionValidator"
