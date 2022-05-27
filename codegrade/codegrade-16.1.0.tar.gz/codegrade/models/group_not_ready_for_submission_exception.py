"""The module that defines the ``GroupNotReadyForSubmissionException`` model.

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
from .user import User


@dataclass
class GroupNotReadyForSubmissionException(BaseError):
    """Exception raised when a group is not yet ready for a submission because
    of the LTI states of the members.
    """

    #: The group of the user.
    group: "Group"
    #: The user that tried to hand in.
    author: "User"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "group",
                    parsers.ParserFor.make(Group),
                    doc="The group of the user.",
                ),
                rqa.RequiredArgument(
                    "author",
                    parsers.ParserFor.make(User),
                    doc="The user that tried to hand in.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "group": to_dict(self.group),
            "author": to_dict(self.author),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GroupNotReadyForSubmissionException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "GroupNotReadyForSubmissionException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            group=parsed.group,
            author=parsed.author,
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
