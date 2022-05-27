"""The module that defines the ``CommentReplyEdit`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .user import User


@dataclass
class CommentReplyEdit:
    """This class represents an edit of a comment reply."""

    #: The id of this edit.
    id: "int"
    #: The moment this edit was created.
    created_at: "datetime.datetime"
    #: The users who edited the comment.
    editor: "User"
    #: The text of the comment before the edit.
    old_text: "str"
    #: The new text after the edit. This will be `None` if this edit represents
    #: a deletion.
    new_text: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this edit.",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment this edit was created.",
            ),
            rqa.RequiredArgument(
                "editor",
                parsers.ParserFor.make(User),
                doc="The users who edited the comment.",
            ),
            rqa.RequiredArgument(
                "old_text",
                rqa.SimpleValue.str,
                doc="The text of the comment before the edit.",
            ),
            rqa.RequiredArgument(
                "new_text",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The new text after the edit. This will be `None` if this"
                    " edit represents a deletion."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "editor": to_dict(self.editor),
            "old_text": to_dict(self.old_text),
            "new_text": to_dict(self.new_text),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CommentReplyEdit"], d: t.Dict[str, t.Any]
    ) -> "CommentReplyEdit":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            created_at=parsed.created_at,
            editor=parsed.editor,
            old_text=parsed.old_text,
            new_text=parsed.new_text,
        )
        res.raw_data = d
        return res
