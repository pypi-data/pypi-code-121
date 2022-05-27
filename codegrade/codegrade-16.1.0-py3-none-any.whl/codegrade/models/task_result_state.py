"""This module defines the enum TaskResultState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class TaskResultState(str, Enum):
    not_started = "not_started"
    started = "started"
    finished = "finished"
    failed = "failed"
    crashed = "crashed"
    skipped = "skipped"
    revoked = "revoked"
