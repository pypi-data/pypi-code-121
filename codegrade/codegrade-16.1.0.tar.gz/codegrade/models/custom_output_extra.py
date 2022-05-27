"""The module that defines the ``CustomOutputExtra`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .custom_output_data import CustomOutputData


@dataclass
class CustomOutputExtra:
    """The extra attrs of a CustomOutput step."""

    #: This is a CustomOutput step.
    type: "t.Literal['custom_output']"
    #: The data for the run program step.
    data: "CustomOutputData"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("custom_output"),
                doc="This is a CustomOutput step.",
            ),
            rqa.RequiredArgument(
                "data",
                parsers.ParserFor.make(CustomOutputData),
                doc="The data for the run program step.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "data": to_dict(self.data),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CustomOutputExtra"], d: t.Dict[str, t.Any]
    ) -> "CustomOutputExtra":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            data=parsed.data,
        )
        res.raw_data = d
        return res
