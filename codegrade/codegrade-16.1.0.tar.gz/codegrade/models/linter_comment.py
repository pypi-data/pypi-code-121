"""The module that defines the ``LinterComment`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LinterComment:
    """A old style linter comment."""

    #: The code produced by the linter. The meaning depends on the linter used.
    code: "str"
    #: The line the comment was placed on.
    line: "int"
    #: The message of the comment.
    msg: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "code",
                rqa.SimpleValue.str,
                doc=(
                    "The code produced by the linter. The meaning depends on"
                    " the linter used."
                ),
            ),
            rqa.RequiredArgument(
                "line",
                rqa.SimpleValue.int,
                doc="The line the comment was placed on.",
            ),
            rqa.RequiredArgument(
                "msg",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The message of the comment.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "code": to_dict(self.code),
            "line": to_dict(self.line),
            "msg": to_dict(self.msg),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LinterComment"], d: t.Dict[str, t.Any]
    ) -> "LinterComment":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            code=parsed.code,
            line=parsed.line,
            msg=parsed.msg,
        )
        res.raw_data = d
        return res
