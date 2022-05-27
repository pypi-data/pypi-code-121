"""The module that defines the ``AutoTestGlobalSetupOutput`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class AutoTestGlobalSetupOutput:
    """This table represents the output of a global setup command."""

    #: The command that was run. If this is `None` this output is for the
    #: configured global setup command.
    cmd: "t.Optional[str]"
    #: The stdout that was produced, is the empty string if no output was
    #: produced.
    stdout: "str"
    #: The stderr that was produced, is the empty string if no output was
    #: produced.
    stderr: "str"
    #: The time spend running the setup. If this is `None` the output is from
    #: before we recorded this value.
    time_spend: "t.Optional[datetime.timedelta]"
    #: The exit code of the command. If this is `None` the output is from
    #: before we recorded this value.
    exit_code: "t.Optional[int]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "cmd",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The command that was run. If this is `None` this output"
                    " is for the configured global setup command."
                ),
            ),
            rqa.RequiredArgument(
                "stdout",
                rqa.SimpleValue.str,
                doc=(
                    "The stdout that was produced, is the empty string if no"
                    " output was produced."
                ),
            ),
            rqa.RequiredArgument(
                "stderr",
                rqa.SimpleValue.str,
                doc=(
                    "The stderr that was produced, is the empty string if no"
                    " output was produced."
                ),
            ),
            rqa.RequiredArgument(
                "time_spend",
                rqa.Nullable(rqa.RichValue.TimeDelta),
                doc=(
                    "The time spend running the setup. If this is `None` the"
                    " output is from before we recorded this value."
                ),
            ),
            rqa.RequiredArgument(
                "exit_code",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The exit code of the command. If this is `None` the"
                    " output is from before we recorded this value."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "cmd": to_dict(self.cmd),
            "stdout": to_dict(self.stdout),
            "stderr": to_dict(self.stderr),
            "time_spend": to_dict(self.time_spend),
            "exit_code": to_dict(self.exit_code),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestGlobalSetupOutput"], d: t.Dict[str, t.Any]
    ) -> "AutoTestGlobalSetupOutput":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            cmd=parsed.cmd,
            stdout=parsed.stdout,
            stderr=parsed.stderr,
            time_spend=parsed.time_spend,
            exit_code=parsed.exit_code,
        )
        res.raw_data = d
        return res
