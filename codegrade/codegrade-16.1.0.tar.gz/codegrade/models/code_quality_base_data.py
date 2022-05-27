"""The module that defines the ``CodeQualityBaseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .code_quality_penalties import CodeQualityPenalties


@dataclass
class CodeQualityBaseData:
    """The base required data for a CodeQuality step."""

    #: The wrapper script.
    wrapper: "t.Literal['cg_checkstyle', 'cg_clang_tidy', 'cg_eslint', 'cg_flake8', 'cg_pmd', 'cg_pylint', 'cg_resharper', 'custom']"
    #: Custom program to run.
    program: "str"
    #: Configuration file.
    config: "str"
    #: Extra arguments.
    args: "str"
    #: Configuration for the amount of penalties per comment.
    penalties: "CodeQualityPenalties"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "wrapper",
                rqa.StringEnum(
                    "cg_checkstyle",
                    "cg_clang_tidy",
                    "cg_eslint",
                    "cg_flake8",
                    "cg_pmd",
                    "cg_pylint",
                    "cg_resharper",
                    "custom",
                ),
                doc="The wrapper script.",
            ),
            rqa.RequiredArgument(
                "program",
                rqa.SimpleValue.str,
                doc="Custom program to run.",
            ),
            rqa.RequiredArgument(
                "config",
                rqa.SimpleValue.str,
                doc="Configuration file.",
            ),
            rqa.RequiredArgument(
                "args",
                rqa.SimpleValue.str,
                doc="Extra arguments.",
            ),
            rqa.RequiredArgument(
                "penalties",
                parsers.ParserFor.make(CodeQualityPenalties),
                doc="Configuration for the amount of penalties per comment.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "wrapper": to_dict(self.wrapper),
            "program": to_dict(self.program),
            "config": to_dict(self.config),
            "args": to_dict(self.args),
            "penalties": to_dict(self.penalties),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CodeQualityBaseData"], d: t.Dict[str, t.Any]
    ) -> "CodeQualityBaseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            wrapper=parsed.wrapper,
            program=parsed.program,
            config=parsed.config,
            args=parsed.args,
            penalties=parsed.penalties,
        )
        res.raw_data = d
        return res
