"""The module that defines the ``ExtendedUser`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .coupon_usage import CouponUsage
from .global_perm_map import GlobalPermMap
from .transaction import Transaction
from .user import User


@dataclass
class ExtendedUser(User):
    """The extended JSON representation of a user."""

    #: The email of the user. This will only be provided for the currently
    #: logged in user.
    email: "str"
    #: Can this user see hidden assignments at least in one course.
    hidden: "bool"
    #: The payments this user did. This will only be provided for the currently
    #: logged in user. For other users it will be an empty list.
    payments: "t.Sequence[Transaction]"
    #: The coupons used by this user. This will only be provided for the
    #: currently logged in user. For other users it will be an empty list.
    used_coupons: "t.Sequence[CouponUsage]"
    #: The permissions of the user. This will only be present if requested.
    permissions: Maybe["GlobalPermMap"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: User.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "email",
                    rqa.SimpleValue.str,
                    doc=(
                        "The email of the user. This will only be provided for"
                        " the currently logged in user."
                    ),
                ),
                rqa.RequiredArgument(
                    "hidden",
                    rqa.SimpleValue.bool,
                    doc=(
                        "Can this user see hidden assignments at least in one"
                        " course."
                    ),
                ),
                rqa.RequiredArgument(
                    "payments",
                    rqa.List(parsers.ParserFor.make(Transaction)),
                    doc=(
                        "The payments this user did. This will only be"
                        " provided for the currently logged in user. For other"
                        " users it will be an empty list."
                    ),
                ),
                rqa.RequiredArgument(
                    "used_coupons",
                    rqa.List(parsers.ParserFor.make(CouponUsage)),
                    doc=(
                        "The coupons used by this user. This will only be"
                        " provided for the currently logged in user. For other"
                        " users it will be an empty list."
                    ),
                ),
                rqa.OptionalArgument(
                    "permissions",
                    parsers.ParserFor.make(GlobalPermMap),
                    doc=(
                        "The permissions of the user. This will only be"
                        " present if requested."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.permissions = maybe_from_nullable(self.permissions)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "email": to_dict(self.email),
            "hidden": to_dict(self.hidden),
            "payments": to_dict(self.payments),
            "used_coupons": to_dict(self.used_coupons),
            "group": to_dict(self.group),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "username": to_dict(self.username),
            "is_test_student": to_dict(self.is_test_student),
            "tenant_id": to_dict(self.tenant_id),
        }
        if self.permissions.is_just:
            res["permissions"] = to_dict(self.permissions.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedUser"], d: t.Dict[str, t.Any]
    ) -> "ExtendedUser":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            email=parsed.email,
            hidden=parsed.hidden,
            payments=parsed.payments,
            used_coupons=parsed.used_coupons,
            group=parsed.group,
            id=parsed.id,
            name=parsed.name,
            username=parsed.username,
            is_test_student=parsed.is_test_student,
            tenant_id=parsed.tenant_id,
            permissions=parsed.permissions,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .group import Group
    from .user_without_group import UserWithoutGroup

    # fmt: on
