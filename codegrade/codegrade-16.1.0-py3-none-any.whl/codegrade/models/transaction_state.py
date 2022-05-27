"""This module defines the enum TransactionState.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class TransactionState(str, Enum):
    pending = "pending"
    success = "success"
    refunding = "refunding"
    refunded = "refunded"
    failed = "failed"
