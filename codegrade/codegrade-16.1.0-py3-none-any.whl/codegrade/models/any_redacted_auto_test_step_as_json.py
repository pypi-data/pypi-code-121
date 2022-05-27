"""The module that defines the ``AnyRedactedAutoTestStepAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .any_auto_test_step_as_json import AnyAutoTestStepAsJSON


@dataclass
class AnyRedactedAutoTestStepAsJSON(AnyAutoTestStepAsJSON):
    """The base JSON for a step when the data is redacted."""

    #: This step is redacted.
    redacted: "t.Literal[True]"
    #: The step type
    type: "t.Literal['check_points', 'code_quality', 'custom_output', 'io_test', 'junit_test', 'run_program']"
    #: The redacted data.
    data: "t.Any"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AnyAutoTestStepAsJSON.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "redacted",
                    rqa.LiteralBoolean(True),
                    doc="This step is redacted.",
                ),
                rqa.RequiredArgument(
                    "type",
                    rqa.StringEnum(
                        "check_points",
                        "code_quality",
                        "custom_output",
                        "io_test",
                        "junit_test",
                        "run_program",
                    ),
                    doc="The step type",
                ),
                rqa.RequiredArgument(
                    "data",
                    rqa.AnyValue,
                    doc="The redacted data.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "redacted": to_dict(self.redacted),
            "type": to_dict(self.type),
            "data": to_dict(self.data),
            "id": to_dict(self.id),
            "description": to_dict(self.description),
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "hidden": to_dict(self.hidden),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AnyRedactedAutoTestStepAsJSON"], d: t.Dict[str, t.Any]
    ) -> "AnyRedactedAutoTestStepAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            redacted=parsed.redacted,
            type=parsed.type,
            data=parsed.data,
            id=parsed.id,
            description=parsed.description,
            name=parsed.name,
            weight=parsed.weight,
            hidden=parsed.hidden,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .auto_test_step_base_as_json import AutoTestStepBaseAsJSON

    # fmt: on
