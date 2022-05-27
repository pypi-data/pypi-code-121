"""The module that defines the ``AssignmentGradingSettingsAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .assignment_grading_scale import AssignmentGradingScale


@dataclass
class AssignmentGradingSettingsAsJSON:
    """JSON representation of the grading settings of this assignment."""

    #: The scale on which this assignment is graded. 'points' means that a
    #: number of points between 0 and 10 (inclusive) can be scored, while with
    #: 'percentage' the score can be between 0 and 100.
    scale: "AssignmentGradingScale"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "scale",
                rqa.EnumValue(AssignmentGradingScale),
                doc=(
                    "The scale on which this assignment is graded. 'points'"
                    " means that a number of points between 0 and 10"
                    " (inclusive) can be scored, while with 'percentage' the"
                    " score can be between 0 and 100."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "scale": to_dict(self.scale),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AssignmentGradingSettingsAsJSON"], d: t.Dict[str, t.Any]
    ) -> "AssignmentGradingSettingsAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            scale=parsed.scale,
        )
        res.raw_data = d
        return res
