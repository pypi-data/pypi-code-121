"""The module that defines the ``ParseAPIException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from ..utils import to_dict
from .base_error import BaseError


@dataclass
class ParseAPIException(BaseError):
    """Exception raised when parsing data failed."""

    #: The parse error that occurred.
    parse_error: "t.Mapping[str, t.Any]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "parse_error",
                    rqa.LookupMapping(rqa.AnyValue),
                    doc="The parse error that occurred.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "parse_error": to_dict(self.parse_error),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ParseAPIException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "ParseAPIException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            parse_error=parsed.parse_error,
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
