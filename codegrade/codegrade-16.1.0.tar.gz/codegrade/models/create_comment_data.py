"""The module that defines the ``CreateCommentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict


@dataclass
class CreateInlineCommentData:
    """ """

    #: Id of the file to place a comment on.
    file_id: "int"
    #: Line in the file to place a comment on.
    line: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "file_id",
                rqa.SimpleValue.int,
                doc="Id of the file to place a comment on.",
            ),
            rqa.RequiredArgument(
                "line",
                rqa.SimpleValue.int,
                doc="Line in the file to place a comment on.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "file_id": to_dict(self.file_id),
            "line": to_dict(self.line),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateInlineCommentData"], d: t.Dict[str, t.Any]
    ) -> "CreateInlineCommentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            file_id=parsed.file_id,
            line=parsed.line,
        )
        res.raw_data = d
        return res


@dataclass
class CreateGeneralCommentData:
    """ """

    #: The work you want to comment on
    work_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "work_id",
                rqa.SimpleValue.int,
                doc="The work you want to comment on",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "work_id": to_dict(self.work_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateGeneralCommentData"], d: t.Dict[str, t.Any]
    ) -> "CreateGeneralCommentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            work_id=parsed.work_id,
        )
        res.raw_data = d
        return res


CreateCommentData = t.Union[
    CreateInlineCommentData,
    CreateGeneralCommentData,
]
CreateCommentDataParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(CreateInlineCommentData),
        ParserFor.make(CreateGeneralCommentData),
    ),
)
