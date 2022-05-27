"""The module that defines the ``FeedbackWithReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .feedback_base import FeedbackBase
from .general_feedback_comment_base import GeneralFeedbackCommentBase
from .inline_feedback_comment_base import InlineFeedbackCommentBase
from .user import User


@dataclass
class FeedbackWithReplies(FeedbackBase):
    """The JSON representation for feedback with replies."""

    #: The feedback of a submission with comments.
    type: "t.Literal['feedback-with-replies']"
    #: The general feedback given on this submission.
    general_comment: "t.Optional[GeneralFeedbackCommentBase]"
    #: A list inline feedback that was given on this submission.
    user: "t.Sequence[InlineFeedbackCommentBase]"
    #: A list of all authors you have permission to see that placed comments.
    #: This list is unique, i.e. each author occurs at most once.
    authors: "t.Sequence[User]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: FeedbackBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "type",
                    rqa.StringEnum("feedback-with-replies"),
                    doc="The feedback of a submission with comments.",
                ),
                rqa.RequiredArgument(
                    "general_comment",
                    rqa.Nullable(
                        parsers.ParserFor.make(GeneralFeedbackCommentBase)
                    ),
                    doc="The general feedback given on this submission.",
                ),
                rqa.RequiredArgument(
                    "user",
                    rqa.List(
                        parsers.ParserFor.make(InlineFeedbackCommentBase)
                    ),
                    doc=(
                        "A list inline feedback that was given on this"
                        " submission."
                    ),
                ),
                rqa.RequiredArgument(
                    "authors",
                    rqa.List(parsers.ParserFor.make(User)),
                    doc=(
                        "A list of all authors you have permission to see that"
                        " placed comments. This list is unique, i.e. each"
                        " author occurs at most once."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "general_comment": to_dict(self.general_comment),
            "user": to_dict(self.user),
            "authors": to_dict(self.authors),
            "general": to_dict(self.general),
            "linter": to_dict(self.linter),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FeedbackWithReplies"], d: t.Dict[str, t.Any]
    ) -> "FeedbackWithReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            general_comment=parsed.general_comment,
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
