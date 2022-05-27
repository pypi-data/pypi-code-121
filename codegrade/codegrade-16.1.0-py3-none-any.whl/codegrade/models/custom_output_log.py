"""The module that defines the ``CustomOutputLog`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .custom_output_log_base import CustomOutputLogBase


@dataclass
class CustomOutputLog(CustomOutputLogBase):
    """The extra fields, only present when a step has not timed-out."""

    #: The amount of points achieved for the step.
    points: Maybe["float"] = Nothing
    #: The part of the stdout that was used to find the amount of points.
    haystack: Maybe["str"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: CustomOutputLogBase.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "points",
                    rqa.SimpleValue.float,
                    doc="The amount of points achieved for the step.",
                ),
                rqa.OptionalArgument(
                    "haystack",
                    rqa.SimpleValue.str,
                    doc=(
                        "The part of the stdout that was used to find the"
                        " amount of points."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.points = maybe_from_nullable(self.points)
        self.haystack = maybe_from_nullable(self.haystack)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "stdout": to_dict(self.stdout),
            "stderr": to_dict(self.stderr),
            "exit_code": to_dict(self.exit_code),
            "time_spend": to_dict(self.time_spend),
        }
        if self.points.is_just:
            res["points"] = to_dict(self.points.value)
        if self.haystack.is_just:
            res["haystack"] = to_dict(self.haystack.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CustomOutputLog"], d: t.Dict[str, t.Any]
    ) -> "CustomOutputLog":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            stdout=parsed.stdout,
            stderr=parsed.stderr,
            exit_code=parsed.exit_code,
            time_spend=parsed.time_spend,
            points=parsed.points,
            haystack=parsed.haystack,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .auto_test_step_log_base import AutoTestStepLogBase

    # fmt: on
