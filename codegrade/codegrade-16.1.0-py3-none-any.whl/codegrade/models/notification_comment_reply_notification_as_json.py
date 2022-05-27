"""The module that defines the ``NotificationCommentReplyNotificationAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_notification import BaseNotification


@dataclass
class NotificationCommentReplyNotificationAsJSON(BaseNotification):
    """The dict used for representing a comment notification as JSON."""

    #: The type of comment that triggered this notification.
    type: "t.Literal['comment_notification']"
    #: The id of the file the comment was placed on.
    file_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseNotification.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "type",
                    rqa.StringEnum("comment_notification"),
                    doc=(
                        "The type of comment that triggered this notification."
                    ),
                ),
                rqa.RequiredArgument(
                    "file_id",
                    rqa.SimpleValue.int,
                    doc="The id of the file the comment was placed on.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "file_id": to_dict(self.file_id),
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
        cls: t.Type["NotificationCommentReplyNotificationAsJSON"],
        d: t.Dict[str, t.Any],
    ) -> "NotificationCommentReplyNotificationAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            file_id=parsed.file_id,
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


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .deleted_comment_reply import DeletedCommentReply
    from .extended_non_deleted_comment_reply import (
        ExtendedNonDeletedCommentReply,
    )
    from .notification_reasons import NotificationReasons

    # fmt: on
