"""This module defines the enum PlagiarismState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class PlagiarismState(str, Enum):
    starting = "starting"
    done = "done"
    crashed = "crashed"
    started = "started"
    parsing = "parsing"
    running = "running"
    finalizing = "finalizing"
    comparing = "comparing"
