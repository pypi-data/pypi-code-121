"""The module that defines the ``ResultDataPostUserLogin`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .extended_user import ExtendedUser


@dataclass
class ResultDataPostUserLogin:
    """When logging in this object will be given."""

    #: The user that was logged in.
    user: "ExtendedUser"
    #: A JWT token that can be used to do authenticated requests.
    access_token: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "user",
                parsers.ParserFor.make(ExtendedUser),
                doc="The user that was logged in.",
            ),
            rqa.RequiredArgument(
                "access_token",
                rqa.SimpleValue.str,
                doc=(
                    "A JWT token that can be used to do authenticated"
                    " requests."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "user": to_dict(self.user),
            "access_token": to_dict(self.access_token),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ResultDataPostUserLogin"], d: t.Dict[str, t.Any]
    ) -> "ResultDataPostUserLogin":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            user=parsed.user,
            access_token=parsed.access_token,
        )
        res.raw_data = d
        return res
