"""The module that defines the ``GeneralFeedbackCommentBaseWithExtendedReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_comment_base_with_extended_replies import (
    BaseCommentBaseWithExtendedReplies,
)
from .general_feedback_extra import GeneralFeedbackExtra


@dataclass
class GeneralFeedbackCommentBaseWithExtendedReplies(
    BaseCommentBaseWithExtendedReplies, GeneralFeedbackExtra
):
    """General feedback with extended replies."""

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCommentBaseWithExtendedReplies.data_parser.parser.combine(
            GeneralFeedbackExtra.data_parser.parser
        )
        .combine(rqa.FixedMapping())
        .use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "replies": to_dict(self.replies),
            "id": to_dict(self.id),
            "work_id": to_dict(self.work_id),
            "type": to_dict(self.type),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GeneralFeedbackCommentBaseWithExtendedReplies"],
        d: t.Dict[str, t.Any],
    ) -> "GeneralFeedbackCommentBaseWithExtendedReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            replies=parsed.replies,
            id=parsed.id,
            work_id=parsed.work_id,
            type=parsed.type,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .base_comment_base import BaseCommentBase
    from .deleted_comment_reply import DeletedCommentReply
    from .extended_non_deleted_comment_reply import (
        ExtendedNonDeletedCommentReply,
    )

    # fmt: on
