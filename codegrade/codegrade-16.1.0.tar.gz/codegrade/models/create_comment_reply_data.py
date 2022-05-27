"""The module that defines the ``CreateCommentReplyData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .comment_reply_type import CommentReplyType


@dataclass
class CreateCommentReplyData:
    """Input data required for the `Comment::CreateReply` operation."""

    #: The content of the reply.
    comment: "str"
    #: The type of reply.
    reply_type: "CommentReplyType"
    #: The comment this was a reply to.
    in_reply_to: Maybe["t.Optional[int]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "comment",
                rqa.SimpleValue.str,
                doc="The content of the reply.",
            ),
            rqa.RequiredArgument(
                "reply_type",
                rqa.EnumValue(CommentReplyType),
                doc="The type of reply.",
            ),
            rqa.OptionalArgument(
                "in_reply_to",
                rqa.Nullable(rqa.SimpleValue.int),
                doc="The comment this was a reply to.",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.in_reply_to = maybe_from_nullable(self.in_reply_to)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "comment": to_dict(self.comment),
            "reply_type": to_dict(self.reply_type),
        }
        if self.in_reply_to.is_just:
            res["in_reply_to"] = to_dict(self.in_reply_to.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateCommentReplyData"], d: t.Dict[str, t.Any]
    ) -> "CreateCommentReplyData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            comment=parsed.comment,
            reply_type=parsed.reply_type,
            in_reply_to=parsed.in_reply_to,
        )
        res.raw_data = d
        return res
