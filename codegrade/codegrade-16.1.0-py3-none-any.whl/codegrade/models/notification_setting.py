"""The module that defines the ``NotificationSetting`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .email_notification_types import EmailNotificationTypes
from .notification_setting_option import NotificationSettingOption


@dataclass
class NotificationSetting:
    """The notification preferences of a user."""

    #: The possible options to set.
    options: "t.Sequence[NotificationSettingOption]"
    #: The possible values for each option.
    possible_values: "t.Sequence[EmailNotificationTypes]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "options",
                rqa.List(parsers.ParserFor.make(NotificationSettingOption)),
                doc="The possible options to set.",
            ),
            rqa.RequiredArgument(
                "possible_values",
                rqa.List(rqa.EnumValue(EmailNotificationTypes)),
                doc="The possible values for each option.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "options": to_dict(self.options),
            "possible_values": to_dict(self.possible_values),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["NotificationSetting"], d: t.Dict[str, t.Any]
    ) -> "NotificationSetting":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            options=parsed.options,
            possible_values=parsed.possible_values,
        )
        res.raw_data = d
        return res
