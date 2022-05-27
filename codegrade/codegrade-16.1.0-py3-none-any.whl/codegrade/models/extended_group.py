"""The module that defines the ``ExtendedGroup`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .group import Group
from .user_without_group import UserWithoutGroup


@dataclass
class ExtendedGroup(Group):
    """The group as extended JSON."""

    #: The virtual user connected to this course. It will not contain the
    #: `group` key as this would lead to an infinite recursion.
    virtual_user: "UserWithoutGroup"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: Group.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "virtual_user",
                    parsers.ParserFor.make(UserWithoutGroup),
                    doc=(
                        "The virtual user connected to this course. It will"
                        " not contain the `group` key as this would lead to an"
                        " infinite recursion."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "virtual_user": to_dict(self.virtual_user),
            "id": to_dict(self.id),
            "members": to_dict(self.members),
            "name": to_dict(self.name),
            "group_set_id": to_dict(self.group_set_id),
            "created_at": to_dict(self.created_at),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedGroup"], d: t.Dict[str, t.Any]
    ) -> "ExtendedGroup":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            virtual_user=parsed.virtual_user,
            id=parsed.id,
            members=parsed.members,
            name=parsed.name,
            group_set_id=parsed.group_set_id,
            created_at=parsed.created_at,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    # fmt: on
