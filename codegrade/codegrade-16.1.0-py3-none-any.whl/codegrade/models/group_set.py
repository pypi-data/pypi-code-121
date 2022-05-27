"""The module that defines the ``GroupSet`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class GroupSet:
    """The way this class will be represented in JSON."""

    #: The id of this group set.
    id: "int"
    #: The minimum size a group should be before it can submit work.
    minimum_size: "int"
    #: The maximum size a group can be.
    maximum_size: "int"
    #: The ids of the assignments connected to this group set.
    assignment_ids: "t.Sequence[int]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this group set.",
            ),
            rqa.RequiredArgument(
                "minimum_size",
                rqa.SimpleValue.int,
                doc=(
                    "The minimum size a group should be before it can submit"
                    " work."
                ),
            ),
            rqa.RequiredArgument(
                "maximum_size",
                rqa.SimpleValue.int,
                doc="The maximum size a group can be.",
            ),
            rqa.RequiredArgument(
                "assignment_ids",
                rqa.List(rqa.SimpleValue.int),
                doc="The ids of the assignments connected to this group set.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "minimum_size": to_dict(self.minimum_size),
            "maximum_size": to_dict(self.maximum_size),
            "assignment_ids": to_dict(self.assignment_ids),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GroupSet"], d: t.Dict[str, t.Any]
    ) -> "GroupSet":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            minimum_size=parsed.minimum_size,
            maximum_size=parsed.maximum_size,
            assignment_ids=parsed.assignment_ids,
        )
        res.raw_data = d
        return res
