"""This module defines the enum FileType.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class FileType(str, Enum):
    file = "file"
    directory = "directory"
