"""This module defines the enum RubricDescriptionType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class RubricDescriptionType(str, Enum):
    plain_text = "plain_text"
    markdown = "markdown"
