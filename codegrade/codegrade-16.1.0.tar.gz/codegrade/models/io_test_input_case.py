"""The module that defines the ``IOTestInputCase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .io_test_option import IOTestOption


@dataclass
class IOTestInputCase:
    """An IOTest input case."""

    #: Name of this sub-step
    name: "str"
    #: Weight of this sub-step
    weight: "float"
    #: Extra arguments to pass to the program for this sub-step
    args: "str"
    #: Input for this sub-step
    stdin: "str"
    #: Expected output of this sub-step
    output: "str"
    #: Matching options for this sub-step
    options: "t.Sequence[IOTestOption]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="Name of this sub-step",
            ),
            rqa.RequiredArgument(
                "weight",
                rqa.SimpleValue.float,
                doc="Weight of this sub-step",
            ),
            rqa.RequiredArgument(
                "args",
                rqa.SimpleValue.str,
                doc="Extra arguments to pass to the program for this sub-step",
            ),
            rqa.RequiredArgument(
                "stdin",
                rqa.SimpleValue.str,
                doc="Input for this sub-step",
            ),
            rqa.RequiredArgument(
                "output",
                rqa.SimpleValue.str,
                doc="Expected output of this sub-step",
            ),
            rqa.RequiredArgument(
                "options",
                rqa.List(rqa.EnumValue(IOTestOption)),
                doc="Matching options for this sub-step",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "args": to_dict(self.args),
            "stdin": to_dict(self.stdin),
            "output": to_dict(self.output),
            "options": to_dict(self.options),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestInputCase"], d: t.Dict[str, t.Any]
    ) -> "IOTestInputCase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            weight=parsed.weight,
            args=parsed.args,
            stdin=parsed.stdin,
            output=parsed.output,
            options=parsed.options,
        )
        res.raw_data = d
        return res
