"""This module defines the enum AutoTestRunnerState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AutoTestRunnerState(str, Enum):
    starting = "starting"
    waiting_for_image = "waiting_for_image"
    running_setup = "running_setup"
    uploading_image = "uploading_image"
    restoring_image = "restoring_image"
    running = "running"
    finished = "finished"
