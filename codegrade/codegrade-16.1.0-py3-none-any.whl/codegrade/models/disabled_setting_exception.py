"""The module that defines the ``DisabledSettingException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .option import Option
from .permission_exception import PermissionException


@dataclass
class DisabledSettingException(PermissionException):
    """Exception raised when a required setting is not enabled."""

    #: The setting that was disabled.
    disabled_setting: "Option"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: PermissionException.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "disabled_setting",
                    parsers.ParserFor.make(Option),
                    doc="The setting that was disabled.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "disabled_setting": to_dict(self.disabled_setting),
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
        cls: t.Type["DisabledSettingException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "DisabledSettingException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            disabled_setting=parsed.disabled_setting,
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
    from .base_error import BaseError
    from .course_permission import CoursePermission
    from .global_permission import GlobalPermission

    # fmt: on
