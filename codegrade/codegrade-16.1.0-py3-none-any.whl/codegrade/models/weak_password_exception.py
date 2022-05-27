"""The module that defines the ``WeakPasswordException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .weak_password_feedback import WeakPasswordFeedback


@dataclass
class WeakPasswordException(BaseError):
    """Exception raised when a password is too weak to be used."""

    #: The feedback on how to improve the password.
    feedback: "WeakPasswordFeedback"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "feedback",
                    parsers.ParserFor.make(WeakPasswordFeedback),
                    doc="The feedback on how to improve the password.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "feedback": to_dict(self.feedback),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["WeakPasswordException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "WeakPasswordException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            feedback=parsed.feedback,
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
