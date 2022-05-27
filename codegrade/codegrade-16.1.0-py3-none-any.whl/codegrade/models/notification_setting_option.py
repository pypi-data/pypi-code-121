"""The module that defines the ``NotificationSettingOption`` model.

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
class NotificationSettingOption:
    """The JSON serialization schema for a single notification setting option."""

    #: The notification reason.
    reason: "NotificationReasons"
    #: The explanation when these kinds of notifications occur.
    explanation: "str"
    #: The current value for this notification reason.
    value: "EmailNotificationTypes"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "reason",
                rqa.EnumValue(NotificationReasons),
                doc="The notification reason.",
            ),
            rqa.RequiredArgument(
                "explanation",
                rqa.SimpleValue.str,
                doc="The explanation when these kinds of notifications occur.",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.EnumValue(EmailNotificationTypes),
                doc="The current value for this notification reason.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "reason": to_dict(self.reason),
            "explanation": to_dict(self.explanation),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["NotificationSettingOption"], d: t.Dict[str, t.Any]
    ) -> "NotificationSettingOption":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            reason=parsed.reason,
            explanation=parsed.explanation,
            value=parsed.value,
        )
        res.raw_data = d
        return res
