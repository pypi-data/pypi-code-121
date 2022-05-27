"""The module that defines the ``LineRange`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LineRange:
    """A line range."""

    #: The line the comment starts (inclusive), one indexed.
    start: "int"
    #: The line the comment ends (inclusive), one indexed.
    end: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "start",
                rqa.SimpleValue.int,
                doc="The line the comment starts (inclusive), one indexed.",
            ),
            rqa.RequiredArgument(
                "end",
                rqa.SimpleValue.int,
                doc="The line the comment ends (inclusive), one indexed.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "start": to_dict(self.start),
            "end": to_dict(self.end),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LineRange"], d: t.Dict[str, t.Any]
    ) -> "LineRange":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            start=parsed.start,
            end=parsed.end,
        )
        res.raw_data = d
        return res
