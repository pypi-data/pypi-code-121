"""The module that defines the ``PutEnrollLinkCourseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class PutEnrollLinkCourseData:
    """Input data required for the `Course::PutEnrollLink` operation."""

    #: The id of the role that users should get when enrolling with this link.
    role_id: "int"
    #: The date this link should stop working.
    expiration_date: "datetime.datetime"
    #: The id of the link to edit, omit to create a new link.
    id: Maybe["str"] = Nothing
    #: Should students be allowed to register a new account using this link.
    #: For registration to actually work this feature should be enabled.
    allow_register: Maybe["bool"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "role_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the role that users should get when enrolling"
                    " with this link."
                ),
            ),
            rqa.RequiredArgument(
                "expiration_date",
                rqa.RichValue.DateTime,
                doc="The date this link should stop working.",
            ),
            rqa.OptionalArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the link to edit, omit to create a new link.",
            ),
            rqa.OptionalArgument(
                "allow_register",
                rqa.SimpleValue.bool,
                doc=(
                    "Should students be allowed to register a new account"
                    " using this link. For registration to actually work this"
                    " feature should be enabled."
                ),
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)
        self.allow_register = maybe_from_nullable(self.allow_register)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "role_id": to_dict(self.role_id),
            "expiration_date": to_dict(self.expiration_date),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        if self.allow_register.is_just:
            res["allow_register"] = to_dict(self.allow_register.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PutEnrollLinkCourseData"], d: t.Dict[str, t.Any]
    ) -> "PutEnrollLinkCourseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            role_id=parsed.role_id,
            expiration_date=parsed.expiration_date,
            id=parsed.id,
            allow_register=parsed.allow_register,
        )
        res.raw_data = d
        return res
