"""The module that defines the ``AnyNonRedactedAutoTestStepAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .any_auto_test_step_as_json import AnyAutoTestStepAsJSON


@dataclass
class AnyNonRedactedAutoTestStepAsJSON(AnyAutoTestStepAsJSON):
    """The base JSON for a step without redacted data."""

    #: This data will be used if the step is not redacted.
    redacted: "t.Literal[False]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AnyAutoTestStepAsJSON.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "redacted",
                    rqa.LiteralBoolean(False),
                    doc="This data will be used if the step is not redacted.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "redacted": to_dict(self.redacted),
            "id": to_dict(self.id),
            "description": to_dict(self.description),
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "hidden": to_dict(self.hidden),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AnyNonRedactedAutoTestStepAsJSON"], d: t.Dict[str, t.Any]
    ) -> "AnyNonRedactedAutoTestStepAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            redacted=parsed.redacted,
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
