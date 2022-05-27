"""The module that defines the ``BaseNotification`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .deleted_comment_reply import DeletedCommentReply
from .extended_non_deleted_comment_reply import ExtendedNonDeletedCommentReply
from .notification_reasons import NotificationReasons


@dataclass
class BaseNotification:
    """The dict used for representing a comment notification as JSON."""

    #: The id of this notification.
    id: "int"
    #: Has this notification been read.
    read: "bool"
    #: The reasons why this notification was sent, this is a list of the two-
    #: tuples where the first element is the reason and the second element an
    #: explanation what this reason means.
    reasons: "t.Sequence[t.Sequence[t.Union[NotificationReasons, str]]]"
    #: The moment the notification was created.
    created_at: "datetime.datetime"
    #: The id of the base comment for which this notification was generated.
    comment_base_id: "int"
    #: The id of the submission (work) the comment was placed on.
    work_id: "int"
    #: The id of the assignment the comment was placed on.
    assignment_id: "int"
    #: The general feedback reply that caused this notification to be
    #: generated.
    comment_reply: "t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this notification.",
            ),
            rqa.RequiredArgument(
                "read",
                rqa.SimpleValue.bool,
                doc="Has this notification been read.",
            ),
            rqa.RequiredArgument(
                "reasons",
                rqa.List(
                    rqa.List(
                        parsers.make_union(
                            rqa.EnumValue(NotificationReasons),
                            rqa.SimpleValue.str,
                        )
                    )
                ),
                doc=(
                    "The reasons why this notification was sent, this is a"
                    " list of the two-tuples where the first element is the"
                    " reason and the second element an explanation what this"
                    " reason means."
                ),
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the notification was created.",
            ),
            rqa.RequiredArgument(
                "comment_base_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the base comment for which this notification"
                    " was generated."
                ),
            ),
            rqa.RequiredArgument(
                "work_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the submission (work) the comment was"
                    " placed on."
                ),
            ),
            rqa.RequiredArgument(
                "assignment_id",
                rqa.SimpleValue.int,
                doc="The id of the assignment the comment was placed on.",
            ),
            rqa.RequiredArgument(
                "comment_reply",
                parsers.make_union(
                    parsers.ParserFor.make(ExtendedNonDeletedCommentReply),
                    parsers.ParserFor.make(DeletedCommentReply),
                ),
                doc=(
                    "The general feedback reply that caused this notification"
                    " to be generated."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "read": to_dict(self.read),
            "reasons": to_dict(self.reasons),
            "created_at": to_dict(self.created_at),
            "comment_base_id": to_dict(self.comment_base_id),
            "work_id": to_dict(self.work_id),
            "assignment_id": to_dict(self.assignment_id),
            "comment_reply": to_dict(self.comment_reply),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseNotification"], d: t.Dict[str, t.Any]
    ) -> "BaseNotification":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            read=parsed.read,
            reasons=parsed.reasons,
            created_at=parsed.created_at,
            comment_base_id=parsed.comment_base_id,
            work_id=parsed.work_id,
            assignment_id=parsed.assignment_id,
            comment_reply=parsed.comment_reply,
        )
        res.raw_data = d
        return res
