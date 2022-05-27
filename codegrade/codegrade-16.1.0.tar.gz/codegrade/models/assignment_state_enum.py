"""This module defines the enum AssignmentStateEnum.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentStateEnum(str, Enum):
    hidden = "hidden"
    open = "open"
    done = "done"
