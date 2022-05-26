from __future__ import annotations

from datetime import datetime
from typing import Optional, Type

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.data_types.timezone import Timezone
from sila2.framework.errors.validation_error import ValidationError
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Timestamp as SilaTimestamp


class Timestamp(DataType[SilaTimestamp, datetime]):
    native_type = datetime
    message_type: Type[SilaTimestamp]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Timestamp
        self.__timezone_field = Timezone(silaframework_pb2_module)

    def to_message(self, dt: datetime, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaTimestamp:
        if not isinstance(dt, datetime):
            raise TypeError("Expected a datetime")
        if dt.tzinfo is None:
            raise ValueError("No timezone provided")

        return self.message_type(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            timezone=self.__timezone_field.to_message(dt.tzinfo),
        )

    def to_native_type(
        self, message: SilaTimestamp, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> datetime:
        if not message.HasField("timezone"):
            raise ValidationError("Date type is missing required field 'timezone'")
        return datetime(
            year=message.year,
            month=message.month,
            day=message.day,
            hour=message.hour,
            minute=message.minute,
            second=message.second,
            tzinfo=self.__timezone_field.to_native_type(message.timezone),
        )

    @staticmethod
    def from_string(value: str) -> datetime:
        if len(value) not in (20, 25):
            raise ValueError(
                f"Invalid timestamp format: '{value}'. "
                f"Must be 'YYYY-MM-DDTHH:MM:SS' plus timezone as 'Z', '-HH:MM' or '+HH:MM'"
            )
        dt = datetime.fromisoformat(value[:19])
        tz = Timezone.from_string(value[19:])
        return datetime(
            year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second, tzinfo=tz
        )
