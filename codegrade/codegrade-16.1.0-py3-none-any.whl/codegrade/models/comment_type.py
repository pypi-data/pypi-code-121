"""This module defines the enum CommentType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class CommentType(str, Enum):
    normal = "normal"
    peer_feedback = "peer_feedback"
