"""The module that defines the ``InlineFeedbackCommentBaseWithExtendedReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_comment_base_with_extended_replies import (
    BaseCommentBaseWithExtendedReplies,
)
from .inline_feedback_extra import InlineFeedbackExtra


@dataclass
class InlineFeedbackCommentBaseWithExtendedReplies(
    InlineFeedbackExtra, BaseCommentBaseWithExtendedReplies
):
    """Inline feedback with extended replies."""

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: InlineFeedbackExtra.data_parser.parser.combine(
            BaseCommentBaseWithExtendedReplies.data_parser.parser
        )
        .combine(rqa.FixedMapping())
        .use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "line": to_dict(self.line),
            "file_id": to_dict(self.file_id),
            "replies": to_dict(self.replies),
            "id": to_dict(self.id),
            "work_id": to_dict(self.work_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["InlineFeedbackCommentBaseWithExtendedReplies"],
        d: t.Dict[str, t.Any],
    ) -> "InlineFeedbackCommentBaseWithExtendedReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            line=parsed.line,
            file_id=parsed.file_id,
            replies=parsed.replies,
            id=parsed.id,
            work_id=parsed.work_id,
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
