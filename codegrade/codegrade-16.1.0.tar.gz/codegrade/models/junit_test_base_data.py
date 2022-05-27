"""The module that defines the ``JunitTestBaseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class JunitTestBaseData:
    """The base data needed for a JunitTest."""

    #: The program to run.
    program: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "program",
                rqa.SimpleValue.str,
                doc="The program to run.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "program": to_dict(self.program),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["JunitTestBaseData"], d: t.Dict[str, t.Any]
    ) -> "JunitTestBaseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            program=parsed.program,
        )
        res.raw_data = d
        return res
