"""The module that defines the ``JunitTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .junit_test_base_data import JunitTestBaseData


@dataclass
class JunitTestData(JunitTestBaseData):
    """The data needed for a JunitTest."""

    #: The wrapper to run.
    wrapper: Maybe[
        "t.Literal['cg_check', 'cg_jest', 'cg_junit4', 'cg_junit5',"
        " 'cg_mocha', 'cg_moxunit', 'cg_phpunit', 'cg_pytest',"
        " 'cg_quickcheck', 'cg_semgrep', 'cg_xunit', 'custom']"
    ] = Nothing
    #: Extra data needed by the frontend
    metadata: Maybe["t.Mapping[str, t.Any]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: JunitTestBaseData.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "wrapper",
                    rqa.StringEnum(
                        "cg_check",
                        "cg_jest",
                        "cg_junit4",
                        "cg_junit5",
                        "cg_mocha",
                        "cg_moxunit",
                        "cg_phpunit",
                        "cg_pytest",
                        "cg_quickcheck",
                        "cg_semgrep",
                        "cg_xunit",
                        "custom",
                    ),
                    doc="The wrapper to run.",
                ),
                rqa.OptionalArgument(
                    "metadata",
                    rqa.LookupMapping(rqa.AnyValue),
                    doc="Extra data needed by the frontend",
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.wrapper = maybe_from_nullable(self.wrapper)
        self.metadata = maybe_from_nullable(self.metadata)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "program": to_dict(self.program),
        }
        if self.wrapper.is_just:
            res["wrapper"] = to_dict(self.wrapper.value)
        if self.metadata.is_just:
            res["metadata"] = to_dict(self.metadata.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["JunitTestData"], d: t.Dict[str, t.Any]
    ) -> "JunitTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            program=parsed.program,
            wrapper=parsed.wrapper,
            metadata=parsed.metadata,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
