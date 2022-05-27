"""The module that defines the ``UserInput`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class UserInput:
    """Data to provide a user by username and tenant."""

    #: The username of the user.
    username: "str"
    #: The id of the tenant of the user, this value will become required
    #: starting with release Nobel.2
    tenant_id: Maybe["str"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "username",
                rqa.SimpleValue.str,
                doc="The username of the user.",
            ),
            rqa.OptionalArgument(
                "tenant_id",
                rqa.SimpleValue.str,
                doc=(
                    "The id of the tenant of the user, this value will become"
                    " required starting with release Nobel.2"
                ),
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.tenant_id = maybe_from_nullable(self.tenant_id)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "username": to_dict(self.username),
        }
        if self.tenant_id.is_just:
            res["tenant_id"] = to_dict(self.tenant_id.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UserInput"], d: t.Dict[str, t.Any]
    ) -> "UserInput":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            username=parsed.username,
            tenant_id=parsed.tenant_id,
        )
        res.raw_data = d
        return res
