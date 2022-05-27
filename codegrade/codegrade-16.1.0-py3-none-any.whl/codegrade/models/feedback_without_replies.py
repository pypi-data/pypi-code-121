"""The module that defines the ``FeedbackWithoutReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .feedback_base import FeedbackBase
from .user import User


@dataclass
class FeedbackWithoutReplies(FeedbackBase):
    """The JSON representation for feedback without replies.

    This representation is considered deprecated, as it doesn't include
    important information (i.e. replies)
    """

    #: This is a deprecated version of the feedback of a submission that omits
    #: any replies.
    type: "t.Literal['feedback-without-replies']"
    #: A mapping between file id and a mapping that is between line and
    #: feedback. So for example: `{5: {0: 'Nice job!'}}` means that file with
    #: `id` 5 has feedback on line 0.
    user: "t.Mapping[str, t.Mapping[str, str]]"
    #: The authors of the user feedback. In the example above the author of the
    #: feedback 'Nice job!' would be at `{5: {0: $USER}}`.
    authors: "t.Mapping[str, t.Mapping[str, User]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: FeedbackBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "type",
                    rqa.StringEnum("feedback-without-replies"),
                    doc=(
                        "This is a deprecated version of the feedback of a"
                        " submission that omits any replies."
                    ),
                ),
                rqa.RequiredArgument(
                    "user",
                    rqa.LookupMapping(rqa.LookupMapping(rqa.SimpleValue.str)),
                    doc=(
                        "A mapping between file id and a mapping that is"
                        " between line and feedback. So for example: `{5: {0:"
                        " 'Nice job!'}}` means that file with `id` 5 has"
                        " feedback on line 0."
                    ),
                ),
                rqa.RequiredArgument(
                    "authors",
                    rqa.LookupMapping(
                        rqa.LookupMapping(parsers.ParserFor.make(User))
                    ),
                    doc=(
                        "The authors of the user feedback. In the example"
                        " above the author of the feedback 'Nice job!' would"
                        " be at `{5: {0: $USER}}`."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "user": to_dict(self.user),
            "authors": to_dict(self.authors),
            "general": to_dict(self.general),
            "linter": to_dict(self.linter),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FeedbackWithoutReplies"], d: t.Dict[str, t.Any]
    ) -> "FeedbackWithoutReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            user=parsed.user,
            authors=parsed.authors,
            general=parsed.general,
            linter=parsed.linter,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .linter_comment import LinterComment

    # fmt: on
