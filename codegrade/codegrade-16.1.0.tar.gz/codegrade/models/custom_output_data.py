"""The module that defines the ``CustomOutputData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CustomOutputData:
    """The data of a CustomOutput step."""

    #: The program to run
    program: "str"
    #: Pattern to used extract the achieved points in the output
    regex: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "program",
                rqa.SimpleValue.str,
                doc="The program to run",
            ),
            rqa.RequiredArgument(
                "regex",
                rqa.SimpleValue.str,
                doc=(
                    "Pattern to used extract the achieved points in the output"
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "program": to_dict(self.program),
            "regex": to_dict(self.regex),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CustomOutputData"], d: t.Dict[str, t.Any]
    ) -> "CustomOutputData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            program=parsed.program,
            regex=parsed.regex,
        )
        res.raw_data = d
        return res
