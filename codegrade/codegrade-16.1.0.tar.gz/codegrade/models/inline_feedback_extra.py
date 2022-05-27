"""The module that defines the ``InlineFeedbackExtra`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class InlineFeedbackExtra:
    """This is inline feedback."""

    #: This is inline feedback.
    type: "t.Literal['inline-feedback']"
    #: The line on which the comment was placed.
    line: "int"
    #: The id of the file on which this comment was placed.
    file_id: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("inline-feedback"),
                doc="This is inline feedback.",
            ),
            rqa.RequiredArgument(
                "line",
                rqa.SimpleValue.int,
                doc="The line on which the comment was placed.",
            ),
            rqa.RequiredArgument(
                "file_id",
                rqa.SimpleValue.str,
                doc="The id of the file on which this comment was placed.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "line": to_dict(self.line),
            "file_id": to_dict(self.file_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["InlineFeedbackExtra"], d: t.Dict[str, t.Any]
    ) -> "InlineFeedbackExtra":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            line=parsed.line,
            file_id=parsed.file_id,
        )
        res.raw_data = d
        return res
