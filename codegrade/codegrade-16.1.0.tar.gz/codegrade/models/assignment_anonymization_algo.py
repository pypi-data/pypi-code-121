"""This module defines the enum AssignmentAnonymizationAlgo.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class AssignmentAnonymizationAlgo(str, Enum):
    murmur_v3 = "murmur_v3"
