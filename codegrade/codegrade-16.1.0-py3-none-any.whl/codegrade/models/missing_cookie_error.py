"""The module that defines the ``MissingCookieError`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .lms_capabilities import LMSCapabilities


@dataclass
class MissingCookieError(BaseError):
    """The exception raised when setting the required LTI 1.3 cookies failed."""

    #: The capabilities of the LMS doing the LTI launch.
    lms_capabilities: "LMSCapabilities"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "lms_capabilities",
                    parsers.ParserFor.make(LMSCapabilities),
                    doc="The capabilities of the LMS doing the LTI launch.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "lms_capabilities": to_dict(self.lms_capabilities),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["MissingCookieError"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "MissingCookieError":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            lms_capabilities=parsed.lms_capabilities,
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
