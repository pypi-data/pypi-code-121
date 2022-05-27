"""The module that defines the ``RunProgramInputAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .auto_test_step_base_input_as_json import AutoTestStepBaseInputAsJSON
from .run_program_extra import RunProgramExtra


@dataclass
class RunProgramInputAsJSON(AutoTestStepBaseInputAsJSON, RunProgramExtra):
    """ """

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestStepBaseInputAsJSON.data_parser.parser.combine(
            RunProgramExtra.data_parser.parser
        )
        .combine(rqa.FixedMapping())
        .use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "hidden": to_dict(self.hidden),
            "type": to_dict(self.type),
            "data": to_dict(self.data),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        if self.description.is_just:
            res["description"] = to_dict(self.description.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RunProgramInputAsJSON"], d: t.Dict[str, t.Any]
    ) -> "RunProgramInputAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            weight=parsed.weight,
            hidden=parsed.hidden,
            id=parsed.id,
            description=parsed.description,
            type=parsed.type,
            data=parsed.data,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from cg_maybe import Maybe, Nothing
    from cg_maybe.utils import maybe_from_nullable

    from .auto_test_step_base_as_json import AutoTestStepBaseAsJSON
    from .run_program_data import RunProgramData

    # fmt: on
