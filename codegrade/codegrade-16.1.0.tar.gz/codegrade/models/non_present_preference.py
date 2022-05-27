"""The module that defines the ``NonPresentPreference`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class NonPresentPreference:
    """Representation of a preference that has not been set by the user."""

    #: Indicates whether the preference was found for the given user.
    present: "t.Literal[False]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "present",
                rqa.LiteralBoolean(False),
                doc=(
                    "Indicates whether the preference was found for the given"
                    " user."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "present": to_dict(self.present),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["NonPresentPreference"], d: t.Dict[str, t.Any]
    ) -> "NonPresentPreference":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            present=parsed.present,
        )
        res.raw_data = d
        return res
