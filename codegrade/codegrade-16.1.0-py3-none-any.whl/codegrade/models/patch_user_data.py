"""The module that defines the ``PatchUserData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class PatchUserData:
    """Input data required for the `User::Patch` operation."""

    #: Your new email
    email: Maybe["str"] = Nothing
    #: Your old password
    old_password: Maybe["str"] = Nothing
    #: Your new name
    name: Maybe["str"] = Nothing
    #: Your new password
    new_password: Maybe["str"] = Nothing
    #: Reset your email on the next LTI launch
    reset_email_on_lti: Maybe["bool"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "email",
                rqa.SimpleValue.str,
                doc="Your new email",
            ),
            rqa.OptionalArgument(
                "old_password",
                rqa.SimpleValue.str,
                doc="Your old password",
            ),
            rqa.OptionalArgument(
                "name",
                rqa.SimpleValue.str,
                doc="Your new name",
            ),
            rqa.OptionalArgument(
                "new_password",
                rqa.SimpleValue.str,
                doc="Your new password",
            ),
            rqa.OptionalArgument(
                "reset_email_on_lti",
                rqa.SimpleValue.bool,
                doc="Reset your email on the next LTI launch",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.email = maybe_from_nullable(self.email)
        self.old_password = maybe_from_nullable(self.old_password)
        self.name = maybe_from_nullable(self.name)
        self.new_password = maybe_from_nullable(self.new_password)
        self.reset_email_on_lti = maybe_from_nullable(self.reset_email_on_lti)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.email.is_just:
            res["email"] = to_dict(self.email.value)
        if self.old_password.is_just:
            res["old_password"] = to_dict(self.old_password.value)
        if self.name.is_just:
            res["name"] = to_dict(self.name.value)
        if self.new_password.is_just:
            res["new_password"] = to_dict(self.new_password.value)
        if self.reset_email_on_lti.is_just:
            res["reset_email_on_lti"] = to_dict(self.reset_email_on_lti.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchUserData"], d: t.Dict[str, t.Any]
    ) -> "PatchUserData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            email=parsed.email,
            old_password=parsed.old_password,
            name=parsed.name,
            new_password=parsed.new_password,
            reset_email_on_lti=parsed.reset_email_on_lti,
        )
        res.raw_data = d
        return res
