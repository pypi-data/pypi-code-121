"""The module that defines the ``UpdateSetAutoTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class UpdateSetAutoTestData:
    """Input data required for the `AutoTest::UpdateSet` operation."""

    #: The minimum percentage a student should have achieved before the next
    #: tests will be run.
    stop_points: Maybe["float"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "stop_points",
                rqa.SimpleValue.float,
                doc=(
                    "The minimum percentage a student should have achieved"
                    " before the next tests will be run."
                ),
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.stop_points = maybe_from_nullable(self.stop_points)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.stop_points.is_just:
            res["stop_points"] = to_dict(self.stop_points.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UpdateSetAutoTestData"], d: t.Dict[str, t.Any]
    ) -> "UpdateSetAutoTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            stop_points=parsed.stop_points,
        )
        res.raw_data = d
        return res
