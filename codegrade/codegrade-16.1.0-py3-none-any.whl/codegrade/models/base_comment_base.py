"""The module that defines the ``BaseCommentBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class BaseCommentBase:
    """A comment thread, this contains many replies which contain the actual
    feedback.
    """

    #: The id of the comment base.
    id: "int"
    #: The id of the work this comment is on. This is always set, also for
    #: inline feedback.
    work_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the comment base.",
            ),
            rqa.RequiredArgument(
                "work_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the work this comment is on. This is always"
                    " set, also for inline feedback."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "work_id": to_dict(self.work_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseCommentBase"], d: t.Dict[str, t.Any]
    ) -> "BaseCommentBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            work_id=parsed.work_id,
        )
        res.raw_data = d
        return res
