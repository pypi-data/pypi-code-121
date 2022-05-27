"""The module that defines the ``BaseError`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .api_codes import APICodes


@dataclass
class BaseError(Exception):
    """The base representation of an APIException."""

    #: The response that generated this error, only present if this data was
    #: parsed as toplevel exception from a response.
    response: t.Optional[Response]
    #: The user readable message for the exception.
    message: "str"
    #: A more detailed version of the error message.
    description: "str"
    #: What type of error is this?
    code: "APICodes"
    #: The id of the request that went wrong. Please include this id when
    #: reporting bugs.
    request_id: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "message",
                rqa.SimpleValue.str,
                doc="The user readable message for the exception.",
            ),
            rqa.RequiredArgument(
                "description",
                rqa.SimpleValue.str,
                doc="A more detailed version of the error message.",
            ),
            rqa.RequiredArgument(
                "code",
                rqa.EnumValue(APICodes),
                doc="What type of error is this?",
            ),
            rqa.RequiredArgument(
                "request_id",
                rqa.SimpleValue.str,
                doc=(
                    "The id of the request that went wrong. Please include"
                    " this id when reporting bugs."
                ),
            ),
        ).use_readable_describe(True)
    )

    def __str__(self) -> str:
        return repr(self)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseError"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "BaseError":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            message=parsed.message,
            description=parsed.description,
            code=parsed.code,
            request_id=parsed.request_id,
            response=response,
        )
        res.raw_data = d
        return res
