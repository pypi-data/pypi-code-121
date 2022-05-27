"""The module that defines the ``WeakPasswordFeedback`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class WeakPasswordFeedback:
    """Feedback on how to improve your password if it is too weak."""

    #: Description why the password is too weak.
    warning: "str"
    #: Suggestions on how to improve the password strength.
    suggestions: "t.Sequence[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "warning",
                rqa.SimpleValue.str,
                doc="Description why the password is too weak.",
            ),
            rqa.RequiredArgument(
                "suggestions",
                rqa.List(rqa.SimpleValue.str),
                doc="Suggestions on how to improve the password strength.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "warning": to_dict(self.warning),
            "suggestions": to_dict(self.suggestions),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["WeakPasswordFeedback"], d: t.Dict[str, t.Any]
    ) -> "WeakPasswordFeedback":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            warning=parsed.warning,
            suggestions=parsed.suggestions,
        )
        res.raw_data = d
        return res
