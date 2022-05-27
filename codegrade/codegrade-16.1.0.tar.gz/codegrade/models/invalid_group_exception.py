"""The module that defines the ``InvalidGroupException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .group import Group


@dataclass
class InvalidGroupException(BaseError):
    """The exception raised when a user does not have a valid group."""

    #: The group that is invalid.
    group: "t.Optional[Group]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "group",
                    rqa.Nullable(parsers.ParserFor.make(Group)),
                    doc="The group that is invalid.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "group": to_dict(self.group),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["InvalidGroupException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "InvalidGroupException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            group=parsed.group,
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
