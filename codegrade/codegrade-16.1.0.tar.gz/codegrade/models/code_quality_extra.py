"""The module that defines the ``CodeQualityExtra`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .code_quality_data import CodeQualityData


@dataclass
class CodeQualityExtra:
    """The extra attrs of a CodeQuality step."""

    #: This is a CodeQuality step.
    type: "t.Literal['code_quality']"
    #: The data for the run program step.
    data: "CodeQualityData"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("code_quality"),
                doc="This is a CodeQuality step.",
            ),
            rqa.RequiredArgument(
                "data",
                parsers.ParserFor.make(CodeQualityData),
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
        cls: t.Type["CodeQualityExtra"], d: t.Dict[str, t.Any]
    ) -> "CodeQualityExtra":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            data=parsed.data,
        )
        res.raw_data = d
        return res
