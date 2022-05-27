"""The module that defines the ``FirstPhaseLTILaunchException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError


@dataclass
class FirstPhaseLTILaunchException(BaseError):
    """The LTI launch went wrong."""

    #: The exception that occurred during the first launch phase.
    original_exception: "t.Optional[BaseError]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "original_exception",
                    rqa.Nullable(parsers.ParserFor.make(BaseError)),
                    doc=(
                        "The exception that occurred during the first launch"
                        " phase."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "original_exception": to_dict(self.original_exception),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FirstPhaseLTILaunchException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "FirstPhaseLTILaunchException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            original_exception=parsed.original_exception,
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
