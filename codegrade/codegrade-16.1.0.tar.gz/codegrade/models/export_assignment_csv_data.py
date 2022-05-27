"""The module that defines the ``ExportAssignmentCSVData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .assignment_export_column import AssignmentExportColumn


@dataclass
class ExportAssignmentCSVData:
    """ """

    #: Export assignment information as a CSV file.
    type: "t.Literal['info']"
    #: The columns that should be included in the report.
    columns: "t.Sequence[AssignmentExportColumn]"
    #: If not `null` only the submissions of these users will be included in
    #: the report.
    user_ids: "t.Optional[t.Sequence[int]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("info"),
                doc="Export assignment information as a CSV file.",
            ),
            rqa.RequiredArgument(
                "columns",
                rqa.List(rqa.EnumValue(AssignmentExportColumn)),
                doc="The columns that should be included in the report.",
            ),
            rqa.RequiredArgument(
                "user_ids",
                rqa.Nullable(rqa.List(rqa.SimpleValue.int)),
                doc=(
                    "If not `null` only the submissions of these users will be"
                    " included in the report."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "columns": to_dict(self.columns),
            "user_ids": to_dict(self.user_ids),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExportAssignmentCSVData"], d: t.Dict[str, t.Any]
    ) -> "ExportAssignmentCSVData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            columns=parsed.columns,
            user_ids=parsed.user_ids,
        )
        res.raw_data = d
        return res
