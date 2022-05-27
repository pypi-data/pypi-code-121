"""This module defines the enum RuleType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class RuleType(str, Enum):
    allow = "allow"
    deny = "deny"
    require = "require"
