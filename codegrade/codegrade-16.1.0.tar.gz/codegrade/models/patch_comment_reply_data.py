"""The module that defines the ``PatchCommentReplyData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PatchCommentReplyData:
    """Input data required for the `Comment::PatchReply` operation."""

    #: The content of the reply.
    comment: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "comment",
                rqa.SimpleValue.str,
                doc="The content of the reply.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "comment": to_dict(self.comment),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchCommentReplyData"], d: t.Dict[str, t.Any]
    ) -> "PatchCommentReplyData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            comment=parsed.comment,
        )
        res.raw_data = d
        return res
