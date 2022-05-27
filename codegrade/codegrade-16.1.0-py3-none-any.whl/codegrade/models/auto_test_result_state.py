"""This module defines the enum AutoTestResultState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AutoTestResultState(str, Enum):
    not_started = "not_started"
    setting_up = "setting_up"
    running_setup = "running_setup"
    running = "running"
    passed = "passed"
    failed = "failed"
    timed_out = "timed_out"
    skipped = "skipped"
