"""The module that defines the ``ExtendedNonDeletedCommentReply`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .non_deleted_comment_reply import NonDeletedCommentReply
from .user import User


@dataclass
class ExtendedNonDeletedCommentReply(NonDeletedCommentReply):
    """The extended version of a reply on a comment thread."""

    #: The author of this reply. This will be `null` if you do not have the
    #: permission to see this information.
    author: "t.Optional[User]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: NonDeletedCommentReply.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "author",
                    rqa.Nullable(parsers.ParserFor.make(User)),
                    doc=(
                        "The author of this reply. This will be `null` if you"
                        " do not have the permission to see this information."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "author": to_dict(self.author),
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
        cls: t.Type["ExtendedNonDeletedCommentReply"], d: t.Dict[str, t.Any]
    ) -> "ExtendedNonDeletedCommentReply":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            author=parsed.author,
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

    from .base_comment_reply import BaseCommentReply
    from .comment_reply_type import CommentReplyType
    from .comment_type import CommentType

    # fmt: on
