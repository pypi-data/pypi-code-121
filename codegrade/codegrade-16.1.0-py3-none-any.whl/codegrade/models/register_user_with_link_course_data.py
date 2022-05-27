"""The module that defines the ``RegisterUserWithLinkCourseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class RegisterUserWithLinkCourseData:
    """Input data required for the `Course::RegisterUserWithLink` operation."""

    #: Username used to log in.
    username: "str"
    #: Password of the new user.
    password: "str"
    #: Email address of the new user.
    email: "str"
    #: Full name of the new user.
    name: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "username",
                rqa.SimpleValue.str,
                doc="Username used to log in.",
            ),
            rqa.RequiredArgument(
                "password",
                rqa.SimpleValue.str,
                doc="Password of the new user.",
            ),
            rqa.RequiredArgument(
                "email",
                rqa.SimpleValue.str,
                doc="Email address of the new user.",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="Full name of the new user.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "username": to_dict(self.username),
            "password": to_dict(self.password),
            "email": to_dict(self.email),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RegisterUserWithLinkCourseData"], d: t.Dict[str, t.Any]
    ) -> "RegisterUserWithLinkCourseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            username=parsed.username,
            password=parsed.password,
            email=parsed.email,
            name=parsed.name,
        )
        res.raw_data = d
        return res
