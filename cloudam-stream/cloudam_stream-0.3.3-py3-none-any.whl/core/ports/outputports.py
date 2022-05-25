from cloudam_stream.core.ports.port import Port
from cloudam_stream.core.payload import Message, Record
from cloudam_stream.core.streams import RedisProducer
from typing import TypeVar, Generic


T = TypeVar("T")


class OutputPort(Generic[T], Port):
    def __init__(self, producer: RedisProducer = None, name=None, actor_name=None):
        if name and actor_name:
            self.channel = actor_name.replace(' ', '_') + '&' + name.replace(' ', '_')
        self.producer = producer
        super().__init__(name, actor_name)

    def encode(self, data: T):
        pass

    def emit(self, data: T):
        self._emit(data)

    def _emit(self, payload: T):
        message_object = Message(payload, "0", type(self).__name__)
        # 转二进制
        msg = message_object.serialize()
        stream_name = self.channel
        self.producer.produce(stream_name, msg)


class TextOutputPort(OutputPort[str]):

    pass


class BinaryOutputPort(OutputPort[bytes]):

    pass


class IntOutputPort(OutputPort[int]):

    pass


class FloatOutputPort(OutputPort[float]):

    pass


class JsonOutputPort(OutputPort[dict]):

    pass


class RecordOutputPort(OutputPort[Record]):

    pass
