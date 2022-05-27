"""The module that defines the ``CommentBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .general_feedback_comment_base import GeneralFeedbackCommentBase
from .inline_feedback_comment_base import InlineFeedbackCommentBase

CommentBase = t.Union[
    InlineFeedbackCommentBase,
    GeneralFeedbackCommentBase,
]
CommentBaseParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(InlineFeedbackCommentBase),
        ParserFor.make(GeneralFeedbackCommentBase),
    ),
)
