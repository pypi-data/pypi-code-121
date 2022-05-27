"""The module that defines the ``CodeQualityPenalties`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CodeQualityPenalties:
    """The penalty config for a code quality comment."""

    #: Penalty for "fatal" comments.
    fatal: "float"
    #: Penalty for "error" comments.
    error: "float"
    #: Penalty for "warning" comments.
    warning: "float"
    #: Penalty for "info" comments.
    info: "float"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "fatal",
                rqa.SimpleValue.float,
                doc='Penalty for "fatal" comments.',
            ),
            rqa.RequiredArgument(
                "error",
                rqa.SimpleValue.float,
                doc='Penalty for "error" comments.',
            ),
            rqa.RequiredArgument(
                "warning",
                rqa.SimpleValue.float,
                doc='Penalty for "warning" comments.',
            ),
            rqa.RequiredArgument(
                "info",
                rqa.SimpleValue.float,
                doc='Penalty for "info" comments.',
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "fatal": to_dict(self.fatal),
            "error": to_dict(self.error),
            "warning": to_dict(self.warning),
            "info": to_dict(self.info),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CodeQualityPenalties"], d: t.Dict[str, t.Any]
    ) -> "CodeQualityPenalties":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            fatal=parsed.fatal,
            error=parsed.error,
            warning=parsed.warning,
            info=parsed.info,
        )
        res.raw_data = d
        return res
