"""The module that defines the ``AutoTestStepBaseInputAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .auto_test_step_base_as_json import AutoTestStepBaseAsJSON


@dataclass
class AutoTestStepBaseInputAsJSON(AutoTestStepBaseAsJSON):
    """The step as JSON."""

    #: The id of the step. Provide this if you want to edit an existing step.
    #: If not provided a new step will be created.
    id: Maybe["int"] = Nothing
    #: Description template for this step that is shown to students.
    description: Maybe["t.Optional[str]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestStepBaseAsJSON.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "id",
                    rqa.SimpleValue.int,
                    doc=(
                        "The id of the step. Provide this if you want to edit"
                        " an existing step. If not provided a new step will be"
                        " created."
                    ),
                ),
                rqa.OptionalArgument(
                    "description",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc=(
                        "Description template for this step that is shown to"
                        " students."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.id = maybe_from_nullable(self.id)
        self.description = maybe_from_nullable(self.description)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "weight": to_dict(self.weight),
            "hidden": to_dict(self.hidden),
        }
        if self.id.is_just:
            res["id"] = to_dict(self.id.value)
        if self.description.is_just:
            res["description"] = to_dict(self.description.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestStepBaseInputAsJSON"], d: t.Dict[str, t.Any]
    ) -> "AutoTestStepBaseInputAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            weight=parsed.weight,
            hidden=parsed.hidden,
            id=parsed.id,
            description=parsed.description,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
