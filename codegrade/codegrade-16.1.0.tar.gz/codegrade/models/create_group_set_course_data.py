"""The module that defines the ``CreateGroupSetCourseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class CreateGroupSetCourseData:
    """Input data required for the `Course::CreateGroupSet` operation."""

    #: The minimum size attribute that the group set should have
    minimum_size: "int"
    #: The maximum size attribute that the group set should have
    maximum_size: "int"
    #: The id of the group to update.
    id: Maybe["int"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "minimum_size",
                rqa.SimpleValue.int,
                doc=(
                    "The minimum size attribute that the group set should have"
                ),
            ),
            rqa.RequiredArgument(
                "maximum_size",
                rqa.SimpleValue.int,
                doc=(
                    "The maximum size attribute that the group set should have"
                ),
            ),
            rqa.OptionalArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the group to update.",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "minimum_size": to_dict(self.minimum_size),
            "maximum_size": to_dict(self.maximum_size),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateGroupSetCourseData"], d: t.Dict[str, t.Any]
    ) -> "CreateGroupSetCourseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            minimum_size=parsed.minimum_size,
            maximum_size=parsed.maximum_size,
            id=parsed.id,
        )
        res.raw_data = d
        return res
