"""The module that defines the ``PresentPreference`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PresentPreference:
    """Representation of a preference that has been set by the user."""

    #: Indicates whether the preference was found for the given user.
    present: "t.Literal[True]"
    #: The current value of the preference.
    value: "t.Any"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "present",
                rqa.LiteralBoolean(True),
                doc=(
                    "Indicates whether the preference was found for the given"
                    " user."
                ),
            ),
            rqa.RequiredArgument(
                "value",
                rqa.AnyValue,
                doc="The current value of the preference.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "present": to_dict(self.present),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PresentPreference"], d: t.Dict[str, t.Any]
    ) -> "PresentPreference":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            present=parsed.present,
            value=parsed.value,
        )
        res.raw_data = d
        return res
