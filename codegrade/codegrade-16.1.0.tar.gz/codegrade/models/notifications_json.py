"""The module that defines the ``NotificationsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .notification import Notification, NotificationParser


@dataclass
class NotificationsJSON:
    """JSON serialization for all notifications."""

    #: The notifications.
    notifications: "t.Sequence[Notification]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "notifications",
                rqa.List(NotificationParser),
                doc="The notifications.",
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
        cls: t.Type["NotificationsJSON"], d: t.Dict[str, t.Any]
    ) -> "NotificationsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            notifications=parsed.notifications,
        )
        res.raw_data = d
        return res
