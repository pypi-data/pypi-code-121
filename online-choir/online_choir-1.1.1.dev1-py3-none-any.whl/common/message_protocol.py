import gzip
import json
import struct


class MessageProtocol:
    def __init__(self, msg):
        self.msg = msg

    @staticmethod
    def get_length(data: bytes) -> int:
        assert len(data) == 2
        length, = struct.unpack('>H', data)
        return length

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(json.loads(gzip.decompress(data).decode('UTF8')))

    def to_bytes(self) -> bytes:
        payload = gzip.compress(json.dumps(self.msg).encode('UTF8'))
        len_b = struct.pack('>H', len(payload))
        return len_b + payload
