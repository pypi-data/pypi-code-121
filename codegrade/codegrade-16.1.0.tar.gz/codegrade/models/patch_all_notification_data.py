"""The module that defines the ``PatchAllNotificationData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PatchAllNotificationData:
    """Input data required for the `Notification::PatchAll` operation."""

    #: The notifications you want to update.
    notifications: "t.Sequence[t.Mapping[str, t.Any]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "notifications",
                rqa.List(rqa.LookupMapping(rqa.AnyValue)),
                doc="The notifications you want to update.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "notifications": to_dict(self.notifications),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchAllNotificationData"], d: t.Dict[str, t.Any]
    ) -> "PatchAllNotificationData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            notifications=parsed.notifications,
        )
        res.raw_data = d
        return res
