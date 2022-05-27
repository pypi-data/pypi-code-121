"""The module that defines the ``Notification`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .notification_comment_reply_notification_as_json import (
    NotificationCommentReplyNotificationAsJSON,
)
from .notification_general_feedback_reply_notification_as_json import (
    NotificationGeneralFeedbackReplyNotificationAsJSON,
)

Notification = t.Union[
    NotificationCommentReplyNotificationAsJSON,
    NotificationGeneralFeedbackReplyNotificationAsJSON,
]
NotificationParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(NotificationCommentReplyNotificationAsJSON),
        ParserFor.make(NotificationGeneralFeedbackReplyNotificationAsJSON),
    ),
)
