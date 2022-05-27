"""The module that defines the ``User`` model.

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
class User(UserWithoutGroup):
    """The JSON representation of a user."""

    #: If this user is a wrapper user for a group this will contain this group,
    #: otherwise it will be `null`.
    group: "t.Optional[Group]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: UserWithoutGroup.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "group",
                    rqa.Nullable(parsers.ParserFor.make(Group)),
                    doc=(
                        "If this user is a wrapper user for a group this will"
                        " contain this group, otherwise it will be `null`."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "group": to_dict(self.group),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "username": to_dict(self.username),
            "is_test_student": to_dict(self.is_test_student),
            "tenant_id": to_dict(self.tenant_id),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["User"], d: t.Dict[str, t.Any]) -> "User":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            group=parsed.group,
            id=parsed.id,
            name=parsed.name,
            username=parsed.username,
            is_test_student=parsed.is_test_student,
            tenant_id=parsed.tenant_id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
