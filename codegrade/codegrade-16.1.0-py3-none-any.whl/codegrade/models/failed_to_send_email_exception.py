"""The module that defines the ``FailedToSendEmailException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .user import User


@dataclass
class FailedToSendEmailException(BaseError):
    """Exception raised when sending some or all emails failed."""

    #: All users that should be emailed.
    all_users: "t.Sequence[User]"
    #: The users where emailing failed.
    failed_users: "t.Sequence[User]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "all_users",
                    rqa.List(parsers.ParserFor.make(User)),
                    doc="All users that should be emailed.",
                ),
                rqa.RequiredArgument(
                    "failed_users",
                    rqa.List(parsers.ParserFor.make(User)),
                    doc="The users where emailing failed.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "all_users": to_dict(self.all_users),
            "failed_users": to_dict(self.failed_users),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FailedToSendEmailException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "FailedToSendEmailException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            all_users=parsed.all_users,
            failed_users=parsed.failed_users,
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
