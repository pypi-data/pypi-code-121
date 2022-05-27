"""The module that defines the ``WorkRubricItem`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .rubric_item import RubricItem


@dataclass
class WorkRubricItem(RubricItem):
    """The connection between a submission and a rubric item."""

    #: The multiplier of this rubric item. This is especially useful for
    #: continuous rows, if a user achieved 50% of the points this will 0.5 for
    #: that rubric row.
    multiplier: "float"
    #: The amount of achieved points in this rubric item. This is simply the
    #: `points` field multiplied by the `multiplier` field.
    achieved_points: "float"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: RubricItem.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "multiplier",
                    rqa.SimpleValue.float,
                    doc=(
                        "The multiplier of this rubric item. This is"
                        " especially useful for continuous rows, if a user"
                        " achieved 50% of the points this will 0.5 for that"
                        " rubric row."
                    ),
                ),
                rqa.RequiredArgument(
                    "achieved_points",
                    rqa.SimpleValue.float,
                    doc=(
                        "The amount of achieved points in this rubric item."
                        " This is simply the `points` field multiplied by the"
                        " `multiplier` field."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "multiplier": to_dict(self.multiplier),
            "achieved_points": to_dict(self.achieved_points),
            "id": to_dict(self.id),
            "description": to_dict(self.description),
            "header": to_dict(self.header),
            "points": to_dict(self.points),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["WorkRubricItem"], d: t.Dict[str, t.Any]
    ) -> "WorkRubricItem":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            multiplier=parsed.multiplier,
            achieved_points=parsed.achieved_points,
            id=parsed.id,
            description=parsed.description,
            header=parsed.header,
            points=parsed.points,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .base_rubric_item import BaseRubricItem

    # fmt: on
