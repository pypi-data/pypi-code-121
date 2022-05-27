"""This module defines the enum CommentReplyType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class CommentReplyType(str, Enum):
    plain_text = "plain_text"
    markdown = "markdown"
