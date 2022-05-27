"""The module that defines the ``CreateGroupGroupSetData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class CreateGroupGroupSetData:
    """Input data required for the `GroupSet::CreateGroup` operation."""

    #: A list of user ids of users that should be the initial members of the
    #: group. This may be an empty list.
    member_ids: "t.Sequence[int]"
    #: The name of the group. This key is optional and a random 'funny' name
    #: will be generated when not given.
    name: Maybe["str"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "member_ids",
                rqa.List(rqa.SimpleValue.int),
                doc=(
                    "A list of user ids of users that should be the initial"
                    " members of the group. This may be an empty list."
                ),
            ),
            rqa.OptionalArgument(
                "name",
                rqa.SimpleValue.str,
                doc=(
                    "The name of the group. This key is optional and a random"
                    " 'funny' name will be generated when not given."
                ),
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.name = maybe_from_nullable(self.name)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "member_ids": to_dict(self.member_ids),
        }
        if self.name.is_just:
            res["name"] = to_dict(self.name.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateGroupGroupSetData"], d: t.Dict[str, t.Any]
    ) -> "CreateGroupGroupSetData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            member_ids=parsed.member_ids,
            name=parsed.name,
        )
        res.raw_data = d
        return res
