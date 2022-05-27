"""The module that defines the ``AutoTestStepBaseAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class AutoTestStepBaseAsJSON:
    """The base JSON for a step, used for both input and output."""

    #: The name of this step.
    name: "str"
    #: The amount of weight this step should have.
    weight: "float"
    #: Is this step hidden? If `true` in most cases students will not be able
    #: to see this step and its details.
    hidden: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of this step.",
            ),
            rqa.RequiredArgument(
                "weight",
                rqa.SimpleValue.float,
                doc="The amount of weight this step should have.",
            ),
            rqa.RequiredArgument(
                "hidden",
                rqa.SimpleValue.bool,
                doc=(
                    "Is this step hidden? If `true` in most cases students"
                    " will not be able to see this step and its details."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "hidden": to_dict(self.hidden),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestStepBaseAsJSON"], d: t.Dict[str, t.Any]
    ) -> "AutoTestStepBaseAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            weight=parsed.weight,
            hidden=parsed.hidden,
        )
        res.raw_data = d
        return res
