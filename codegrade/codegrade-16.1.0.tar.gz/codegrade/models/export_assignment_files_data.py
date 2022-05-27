"""The module that defines the ``ExportAssignmentFilesData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class ExportAssignmentFilesData:
    """ """

    #: Export submissions as zip.
    type: "t.Literal['files']"
    #: If not `null` only the submissions of these users will be exported.
    user_ids: "t.Optional[t.Sequence[int]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("files"),
                doc="Export submissions as zip.",
            ),
            rqa.RequiredArgument(
                "user_ids",
                rqa.Nullable(rqa.List(rqa.SimpleValue.int)),
                doc=(
                    "If not `null` only the submissions of these users will be"
                    " exported."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "user_ids": to_dict(self.user_ids),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExportAssignmentFilesData"], d: t.Dict[str, t.Any]
    ) -> "ExportAssignmentFilesData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            user_ids=parsed.user_ids,
        )
        res.raw_data = d
        return res
