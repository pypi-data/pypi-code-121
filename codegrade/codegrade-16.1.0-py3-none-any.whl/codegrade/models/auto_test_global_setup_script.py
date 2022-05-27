"""The module that defines the ``AutoTestGlobalSetupScript`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class AutoTestGlobalSetupScript:
    """This class represents a command that will be run as the global setup."""

    #: This was the command that was provided by the user. Only this command is
    #: editable.
    user_provided: "bool"
    #: The command that will be executed.
    cmd: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "user_provided",
                rqa.SimpleValue.bool,
                doc=(
                    "This was the command that was provided by the user. Only"
                    " this command is editable."
                ),
            ),
            rqa.RequiredArgument(
                "cmd",
                rqa.SimpleValue.str,
                doc="The command that will be executed.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "user_provided": to_dict(self.user_provided),
            "cmd": to_dict(self.cmd),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestGlobalSetupScript"], d: t.Dict[str, t.Any]
    ) -> "AutoTestGlobalSetupScript":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            user_provided=parsed.user_provided,
            cmd=parsed.cmd,
        )
        res.raw_data = d
        return res
