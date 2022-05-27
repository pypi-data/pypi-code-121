"""The module that defines the ``GeneralFeedbackExtra`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class GeneralFeedbackExtra:
    """This is general feedback."""

    #: This is general feedback.
    type: "t.Literal['general-feedback']"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("general-feedback"),
                doc="This is general feedback.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GeneralFeedbackExtra"], d: t.Dict[str, t.Any]
    ) -> "GeneralFeedbackExtra":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
        )
        res.raw_data = d
        return res
