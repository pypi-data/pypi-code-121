"""The module that defines the ``CommentReply`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .deleted_comment_reply import DeletedCommentReply
from .non_deleted_comment_reply import NonDeletedCommentReply

CommentReply = t.Union[
    NonDeletedCommentReply,
    DeletedCommentReply,
]
CommentReplyParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(NonDeletedCommentReply),
        ParserFor.make(DeletedCommentReply),
    ),
)
