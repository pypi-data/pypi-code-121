"""This module defines the enum NotificationReasons.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class NotificationReasons(str, Enum):
    assignee = "assignee"
    author = "author"
    replied = "replied"
