from __future__ import annotations

from datetime import timedelta
from typing import Optional

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Duration as SilaDuration


class Duration(MessageMappable[SilaDuration, timedelta]):
    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.Duration

    def to_native_type(
        self, message: SilaDuration, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> timedelta:
        return timedelta(seconds=message.seconds, microseconds=round(message.nanos / 1000))

    def to_message(self, duration: timedelta, toplevel_named_data_node: Optional[NamedDataNode] = None) -> SilaDuration:
        seconds, rest = divmod(duration.total_seconds(), 1)
        return self.message_type(seconds=round(seconds), nanos=round(rest * 1e9))
