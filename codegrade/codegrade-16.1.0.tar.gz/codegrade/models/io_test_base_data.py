"""The module that defines the ``IOTestBaseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .io_test_input_case import IOTestInputCase


@dataclass
class IOTestBaseData:
    """The base data of an IOTest."""

    #: Program to run for each sub-step
    program: "str"
    #: Configuration of the sub-steps
    inputs: "t.Sequence[IOTestInputCase]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "program",
                rqa.SimpleValue.str,
                doc="Program to run for each sub-step",
            ),
            rqa.RequiredArgument(
                "inputs",
                rqa.List(parsers.ParserFor.make(IOTestInputCase)),
                doc="Configuration of the sub-steps",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "program": to_dict(self.program),
            "inputs": to_dict(self.inputs),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestBaseData"], d: t.Dict[str, t.Any]
    ) -> "IOTestBaseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            program=parsed.program,
            inputs=parsed.inputs,
        )
        res.raw_data = d
        return res
