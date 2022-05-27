"""This module defines the enum QualityCommentSeverity.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class QualityCommentSeverity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"
    fatal = "fatal"
