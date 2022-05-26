from __future__ import annotations

from datetime import time
from typing import Optional, Type

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.data_types.timezone import Timezone
from sila2.framework.errors.validation_error import ValidationError
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Time as SilaTime


class Time(DataType[SilaTime, time]):
    native_type = time
    message_type: Type[SilaTime]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Time
        self.__timezone_field = Timezone(silaframework_pb2_module)

    def to_message(self, t: time, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaTime:
        if not isinstance(t, time):
            raise TypeError("Expected a time")
        if t.tzinfo is None:
            raise ValueError("No timezone provided")

        return self.message_type(
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            timezone=self.__timezone_field.to_message(t.tzinfo),
        )

    def to_native_type(self, message: SilaTime, toplevel_named_data_node: Optional[NamedDataNode] = None) -> time:
        if not message.HasField("timezone"):
            raise ValidationError("Date type is missing required field 'timezone'")
        return time(
            hour=message.hour,
            minute=message.minute,
            second=message.second,
            tzinfo=self.__timezone_field.to_native_type(message.timezone),
        )

    @staticmethod
    def from_string(value: str) -> time:
        t = time.fromisoformat(value[:8])
        tz = Timezone.from_string(value[8:])
        return time(hour=t.hour, minute=t.minute, second=t.second, tzinfo=tz)
