from __future__ import annotations

import re
from datetime import timedelta, timezone, tzinfo
from typing import Optional, Type

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Timezone as SilaTimezone


class Timezone(MessageMappable):
    native_type = tzinfo
    message_type: Type[SilaTimezone]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Timezone

    def to_message(self, tz: tzinfo, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaTimezone:
        offset_timedelta = tz.utcoffset(None)

        offset_seconds = offset_timedelta.total_seconds()
        if int(offset_seconds) % 60 != 0:
            raise ValueError("SiLA2 does not support seconds in Timezone")

        offset_hours, offset_minutes = divmod(offset_seconds // 60, 60)

        return self.message_type(hours=int(offset_hours), minutes=int(offset_minutes))

    def to_native_type(
        self, message: SilaTimezone, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> timezone:
        return timezone(timedelta(hours=message.hours, minutes=message.minutes))

    @staticmethod
    def from_string(value: str) -> tzinfo:
        if value == "Z":
            return timezone(timedelta(hours=0, minutes=0))
        if not re.match("^[+-][0-9]{2}:[0-9]{2}$", value):
            raise ValueError(f"Invalid timezone format: '{value}'. Must be 'Z' or like '+HH:MM' or '-HH:MM'")

        td = timedelta(hours=int(value[1:3]), minutes=int(value[-2:]))
        sign = int(value[0] + "1")
        td = td * sign

        if abs(td) > timedelta(hours=14):
            raise ValueError(f"Timezone UTC offset must be between -14:00 and +14:00, was {td}")

        return timezone(td)
