"""The module that defines the ``BaseCommentReply`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .comment_reply_type import CommentReplyType
from .comment_type import CommentType


@dataclass
class BaseCommentReply:
    """A reply on a comment thread."""

    #: The id of the reply
    id: "int"
    #: If this reply was a reply to a specific `CommentReply`, this field will
    #: be the id of this `CommentReply`. Otherwise this will be `null`.
    in_reply_to_id: "t.Optional[int]"
    #: The date the last edit was made to this reply, this will be `null` if
    #: you do not have the permission to see this information.
    last_edit: "t.Optional[datetime.datetime]"
    #: The date this reply was created.
    created_at: "datetime.datetime"
    #: The formatting that the content of this reply is in.
    reply_type: "CommentReplyType"
    #: The type of comment this is.
    comment_type: "CommentType"
    #: Is this comment approved (i.e. visible for the author of the submission
    #: in most cases) or not.
    approved: "bool"
    #: The id of the `CommentBase` this reply is in.
    comment_base_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the reply",
            ),
            rqa.RequiredArgument(
                "in_reply_to_id",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "If this reply was a reply to a specific `CommentReply`,"
                    " this field will be the id of this `CommentReply`."
                    " Otherwise this will be `null`."
                ),
            ),
            rqa.RequiredArgument(
                "last_edit",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The date the last edit was made to this reply, this will"
                    " be `null` if you do not have the permission to see this"
                    " information."
                ),
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The date this reply was created.",
            ),
            rqa.RequiredArgument(
                "reply_type",
                rqa.EnumValue(CommentReplyType),
                doc="The formatting that the content of this reply is in.",
            ),
            rqa.RequiredArgument(
                "comment_type",
                rqa.EnumValue(CommentType),
                doc="The type of comment this is.",
            ),
            rqa.RequiredArgument(
                "approved",
                rqa.SimpleValue.bool,
                doc=(
                    "Is this comment approved (i.e. visible for the author of"
                    " the submission in most cases) or not."
                ),
            ),
            rqa.RequiredArgument(
                "comment_base_id",
                rqa.SimpleValue.int,
                doc="The id of the `CommentBase` this reply is in.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
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
        cls: t.Type["BaseCommentReply"], d: t.Dict[str, t.Any]
    ) -> "BaseCommentReply":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
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
