"""This module defines the enum Currency.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class Currency(str, Enum):
    eur = "eur"
    usd = "usd"
    gbp = "gbp"
