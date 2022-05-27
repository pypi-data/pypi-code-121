"""This module defines the enum TaxBehavior.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class TaxBehavior(str, Enum):
    inclusive = "inclusive"
    exclusive = "exclusive"
    disabled = "disabled"
