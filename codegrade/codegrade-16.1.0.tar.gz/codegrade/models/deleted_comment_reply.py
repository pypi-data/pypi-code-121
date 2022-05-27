"""The module that defines the ``DeletedCommentReply`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_comment_reply import BaseCommentReply


@dataclass
class DeletedCommentReply(BaseCommentReply):
    """A deleted reply on a comment thread."""

    #: Whether this reply is deleted.
    deleted: "t.Literal[True]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCommentReply.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "deleted",
                    rqa.LiteralBoolean(True),
                    doc="Whether this reply is deleted.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
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
        cls: t.Type["DeletedCommentReply"], d: t.Dict[str, t.Any]
    ) -> "DeletedCommentReply":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
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
