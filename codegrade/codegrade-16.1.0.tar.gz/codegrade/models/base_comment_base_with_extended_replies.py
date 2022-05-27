"""The module that defines the ``BaseCommentBaseWithExtendedReplies`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .base_comment_base import BaseCommentBase
from .deleted_comment_reply import DeletedCommentReply
from .extended_non_deleted_comment_reply import ExtendedNonDeletedCommentReply


@dataclass
class BaseCommentBaseWithExtendedReplies(BaseCommentBase):
    """A comment base that contains extended replies."""

    #: These are the extended replies on this comment base.
    replies: "t.Sequence[t.Union[ExtendedNonDeletedCommentReply, DeletedCommentReply]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseCommentBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "replies",
                    rqa.List(
                        parsers.make_union(
                            parsers.ParserFor.make(
                                ExtendedNonDeletedCommentReply
                            ),
                            parsers.ParserFor.make(DeletedCommentReply),
                        )
                    ),
                    doc="These are the extended replies on this comment base.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "replies": to_dict(self.replies),
            "id": to_dict(self.id),
            "work_id": to_dict(self.work_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseCommentBaseWithExtendedReplies"],
        d: t.Dict[str, t.Any],
    ) -> "BaseCommentBaseWithExtendedReplies":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            replies=parsed.replies,
            id=parsed.id,
            work_id=parsed.work_id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
