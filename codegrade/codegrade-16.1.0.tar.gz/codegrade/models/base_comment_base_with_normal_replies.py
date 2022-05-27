"""The module that defines the ``BaseCommentBaseWithNormalReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .base_comment_base import BaseCommentBase
from .comment_reply import CommentReply, CommentReplyParser


@dataclass
class BaseCommentBaseWithNormalReplies(BaseCommentBase):
    """A comment base that contains normal (i.e. non extended) replies."""

    #: These are the normal replies on this comment base.
    replies: "t.Sequence[CommentReply]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCommentBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "replies",
                    rqa.List(CommentReplyParser),
                    doc="These are the normal replies on this comment base.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "replies": to_dict(self.replies),
            "id": to_dict(self.id),
            "work_id": to_dict(self.work_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseCommentBaseWithNormalReplies"], d: t.Dict[str, t.Any]
    ) -> "BaseCommentBaseWithNormalReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            replies=parsed.replies,
            id=parsed.id,
            work_id=parsed.work_id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
