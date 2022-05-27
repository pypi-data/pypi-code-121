"""This module defines the enum AutoTestStepResultState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AutoTestStepResultState(str, Enum):
    not_started = "not_started"
    running = "running"
    passed = "passed"
    failed = "failed"
    timed_out = "timed_out"
    skipped = "skipped"
