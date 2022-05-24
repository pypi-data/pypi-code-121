from cloudam_stream.core.ports.port import Port
from cloudam_stream.core.payload import Record
import json
from typing import TypeVar, Generic


T = TypeVar("T")


class InputPort(Generic[T], Port):

    def parse(self, message) -> T:
        return message

    # 关联port
    def connect(self, upstream_actor_name, upstream_port_name):
        self.upstream_actor = upstream_actor_name
        self.upstream_port = upstream_port_name
        self.channel = upstream_actor_name.replace(' ', '_') + '&' + upstream_port_name.replace(' ', '_')


class BinaryInputPort(InputPort[bytes]):

    pass


class TextInputPort(InputPort[str]):

    pass


class FloatInputPort(InputPort[float]):

    pass


class JsonInputPort(InputPort[json]):

    def parse(self, message) -> json:
        return json.loads(message)


class RecordInputPort(InputPort[Record]):

    pass







