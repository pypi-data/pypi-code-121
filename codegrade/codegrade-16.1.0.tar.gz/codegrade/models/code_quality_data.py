"""The module that defines the ``CodeQualityData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .code_quality_base_data import CodeQualityBaseData


@dataclass
class CodeQualityData(CodeQualityBaseData):
    """The data for a CodeQuality step."""

    #: Ignore comments whose file could not be found in the submission instead
    #: of raising an error.
    ignore_files_not_found: Maybe["bool"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: CodeQualityBaseData.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "ignore_files_not_found",
                    rqa.SimpleValue.bool,
                    doc=(
                        "Ignore comments whose file could not be found in the"
                        " submission instead of raising an error."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.ignore_files_not_found = maybe_from_nullable(
            self.ignore_files_not_found
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "wrapper": to_dict(self.wrapper),
            "program": to_dict(self.program),
            "config": to_dict(self.config),
            "args": to_dict(self.args),
            "penalties": to_dict(self.penalties),
        }
        if self.ignore_files_not_found.is_just:
            res["ignore_files_not_found"] = to_dict(
                self.ignore_files_not_found.value
            )
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CodeQualityData"], d: t.Dict[str, t.Any]
    ) -> "CodeQualityData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            wrapper=parsed.wrapper,
            program=parsed.program,
            config=parsed.config,
            args=parsed.args,
            penalties=parsed.penalties,
            ignore_files_not_found=parsed.ignore_files_not_found,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .code_quality_penalties import CodeQualityPenalties

    # fmt: on
