"""The module that defines the ``PatchNotificationSettingUserSettingData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .email_notification_types import EmailNotificationTypes
from .notification_reasons import NotificationReasons


@dataclass
class PatchNotificationSettingUserSettingData:
    """Input data required for the `User Setting::PatchNotificationSetting`
    operation.
    """

    #: For what type notification do you want to change the settings.
    reason: "NotificationReasons"
    #: The new value of the notification setting.
    value: "EmailNotificationTypes"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "reason",
                rqa.EnumValue(NotificationReasons),
                doc=(
                    "For what type notification do you want to change the"
                    " settings."
                ),
            ),
            rqa.RequiredArgument(
                "value",
                rqa.EnumValue(EmailNotificationTypes),
                doc="The new value of the notification setting.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "reason": to_dict(self.reason),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchNotificationSettingUserSettingData"],
        d: t.Dict[str, t.Any],
    ) -> "PatchNotificationSettingUserSettingData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            reason=parsed.reason,
            value=parsed.value,
        )
        res.raw_data = d
        return res
