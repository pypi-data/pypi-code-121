"""The module that defines the ``NonDeletedCommentReply`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_comment_reply import BaseCommentReply


@dataclass
class NonDeletedCommentReply(BaseCommentReply):
    """A reply on a comment thread."""

    #: The content of the reply, see `reply_type` to check in what kind of
    #: formatting this reply is.
    comment: "str"
    #: The id of the author of this reply, this will be `null` if no author is
    #: known (for legacy replies), or if you do not have the permission to see
    #: the author.
    author_id: "t.Optional[int]"
    #: Whether this reply is deleted.
    deleted: "t.Literal[False]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCommentReply.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "comment",
                    rqa.SimpleValue.str,
                    doc=(
                        "The content of the reply, see `reply_type` to check"
                        " in what kind of formatting this reply is."
                    ),
                ),
                rqa.RequiredArgument(
                    "author_id",
                    rqa.Nullable(rqa.SimpleValue.int),
                    doc=(
                        "The id of the author of this reply, this will be"
                        " `null` if no author is known (for legacy replies),"
                        " or if you do not have the permission to see the"
                        " author."
                    ),
                ),
                rqa.RequiredArgument(
                    "deleted",
                    rqa.LiteralBoolean(False),
                    doc="Whether this reply is deleted.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "comment": to_dict(self.comment),
            "author_id": to_dict(self.author_id),
            "deleted": to_dict(self.deleted),
            "id": to_dict(self.id),
            "in_reply_to_id": to_dict(self.in_reply_to_id),
            "last_edit": to_dict(self.last_edit),
            "created_at": to_dict(self.created_at),
            "reply_type": to_dict(self.reply_type),
            "comment_type": to_dict(self.comment_type),
            "approved": to_dict(self.approved),
            "comment_base_id": to_dict(self.comment_base_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["NonDeletedCommentReply"], d: t.Dict[str, t.Any]
    ) -> "NonDeletedCommentReply":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            comment=parsed.comment,
            author_id=parsed.author_id,
            deleted=parsed.deleted,
            id=parsed.id,
            in_reply_to_id=parsed.in_reply_to_id,
            last_edit=parsed.last_edit,
            created_at=parsed.created_at,
            reply_type=parsed.reply_type,
            comment_type=parsed.comment_type,
            approved=parsed.approved,
            comment_base_id=parsed.comment_base_id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .comment_reply_type import CommentReplyType
    from .comment_type import CommentType

    # fmt: on
