"""This module defines the enum EmailNotificationTypes.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class EmailNotificationTypes(str, Enum):
    direct = "direct"
    daily = "daily"
    weekly = "weekly"
    off = "off"
