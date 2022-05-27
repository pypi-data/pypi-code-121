"""The module that defines the ``ExportAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .export_assignment_csv_data import ExportAssignmentCSVData
from .export_assignment_files_data import ExportAssignmentFilesData

ExportAssignmentData = t.Union[
    ExportAssignmentCSVData,
    ExportAssignmentFilesData,
]
ExportAssignmentDataParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(ExportAssignmentCSVData),
        ParserFor.make(ExportAssignmentFilesData),
    ),
)
