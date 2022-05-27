"""The module that defines the ``PermissionException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .course_permission import CoursePermission
from .global_permission import GlobalPermission


@dataclass
class PermissionException(BaseError):
    """Exception raised when a permission check fails."""

    #: If the exception was caused by missing permissions this will be a list
    #: of permissions that are missing. You might not need all permissions in
    #: this list.
    missing_permissions: "t.Optional[t.Sequence[t.Union[GlobalPermission, CoursePermission]]]"
    #: The id of the user that does not have the permission.
    user_id: "t.Optional[int]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "missing_permissions",
                    rqa.Nullable(
                        rqa.List(
                            parsers.make_union(
                                rqa.EnumValue(GlobalPermission),
                                rqa.EnumValue(CoursePermission),
                            )
                        )
                    ),
                    doc=(
                        "If the exception was caused by missing permissions"
                        " this will be a list of permissions that are missing."
                        " You might not need all permissions in this list."
                    ),
                ),
                rqa.RequiredArgument(
                    "user_id",
                    rqa.Nullable(rqa.SimpleValue.int),
                    doc=(
                        "The id of the user that does not have the permission."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "missing_permissions": to_dict(self.missing_permissions),
            "user_id": to_dict(self.user_id),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PermissionException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "PermissionException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            missing_permissions=parsed.missing_permissions,
            user_id=parsed.user_id,
            message=parsed.message,
            description=parsed.description,
            code=parsed.code,
            request_id=parsed.request_id,
            response=response,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .api_codes import APICodes

    # fmt: on
