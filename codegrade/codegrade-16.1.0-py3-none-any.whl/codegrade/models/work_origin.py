"""This module defines the enum WorkOrigin.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class WorkOrigin(str, Enum):
    uploaded_files = "uploaded_files"
    github = "github"
    gitlab = "gitlab"
