"""The module that defines the ``CheckPointsData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CheckPointsData:
    """The data of a CheckPoints step."""

    #: The minimal amount of points required to pass the check
    min_points: "float"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "min_points",
                rqa.SimpleValue.float,
                doc="The minimal amount of points required to pass the check",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "min_points": to_dict(self.min_points),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CheckPointsData"], d: t.Dict[str, t.Any]
    ) -> "CheckPointsData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            min_points=parsed.min_points,
        )
        res.raw_data = d
        return res
