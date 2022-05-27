"""The module that defines the ``FileTree`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .base_file import BaseFile
from .directory_with_children import DirectoryWithChildren

FileTree = t.Union[
    BaseFile,
    DirectoryWithChildren,
]
FileTreeParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(BaseFile), ParserFor.make(DirectoryWithChildren)
    ),
)
