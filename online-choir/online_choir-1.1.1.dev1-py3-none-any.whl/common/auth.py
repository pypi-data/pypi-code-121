import struct

from .constants import VOCAL_GROUPS
from .version import VERSION

HEADER_SIZE = 512
AUTH_KEY = b'\xb7#\xd2\x9b\xdf\x8b\xd0\xb4\x10\xdf\xdf\xfe^\xa6\xc7\x83W\xf1\xfe\xf8\xe7\xe1\xee\xac/\x90Un\x83\xe1\\"\x84\xe0\xaf\xa0:\x06\x90\xbe\xca\'\xe5\x80\x9c\x17\xfegcZ\t\x9e\x86lu\x11.?\xfcf\xa1\xbf\x9c\x1a\xef\x0c;\xb6r\x0e\xeaSk\x0e\x9c[\x81\x92X\xc2Uo\x82T\r\xc3\xba\xac@7\t\x8f\xca~\x8a}\xdd\rh\xa3\x05m\x7f\xbd\x83\xc4\x86c\xf0\\9\x15s\x1d\x8d\xf8\xf4\xf8\x81\xe4xU\xb6i\xe7w\xd9\xe4\xe8\xf6"\x10\xcd\x0e\xc7\xf9$\x84I;5\xb4K\x98\xae/d6\xce\x88?\x86\x94\\\xf1\xf9\xf8A\xa6\xd5p\x1c\xce>\xe9\xd9\x03\xbfu3D\x8f\xafTV6Zc\x85*\xb9\xec\xb8\xbb\xdc\x1fi\x89mb\xc5\x93-\xa7h \x99\xad\xfc\x86^\x9f\x94\xd2\xd3\xe5D\xa6\x0f\xcc\xb0\x10\x03\xe8-t\xed3\xc2\xc0\x85\x08\x03\x1ai\xdc]v\xacGG\xea\xccH\xfe\xc9UM&U\x0cj+!\x91a[I\xc8\x8c\xc9H\xd4M\xfaw'
PROTOCOL_VERSION = 3


class AuthenticationHeader:
    def __init__(self, name='', group='', client_version=VERSION, valid=True):
        self.is_valid = valid
        self.name = name
        self.group = group
        self.client_version = client_version

    @classmethod
    def bad_header(cls):
        return cls(valid=False)

    @classmethod
    def from_bytes(cls, data: bytes):
        version, = struct.unpack('>H', data[:2])
        key = data[HEADER_SIZE - len(AUTH_KEY):HEADER_SIZE]
        if key != AUTH_KEY:
            return cls.bad_header()
        if version == 1:
            name = ''
            group = VOCAL_GROUPS[0]
            client_version = 'Unknown (1)'
        elif version == 2:
            name = cls.decode_field(data[2:244], '')
            group = cls.decode_field(data[244:256], VOCAL_GROUPS[0])
            client_version = 'Unknown (2)'
        elif version == PROTOCOL_VERSION:
            name = cls.decode_field(data[2:220], '')
            client_version = cls.decode_field(data[220:244], 'Unknown (3)')
            group = cls.decode_field(data[244:256], VOCAL_GROUPS[0])
        else:
            return cls.bad_header()
        return cls(name, group, client_version)

    def to_bytes(self) -> bytes:
        version_b = struct.pack('>H', PROTOCOL_VERSION)
        name_b = self.encode_field(self.name, 218)
        client_version_b = self.encode_field(self.client_version, 24)
        group_b = self.encode_field(self.group, 12)
        return version_b + name_b + client_version_b + group_b + AUTH_KEY

    @staticmethod
    def encode_field(value: str, length: int) -> bytes:
        return value.encode('UTF8')[:length].ljust(length)

    @staticmethod
    def decode_field(data: bytes, default: str) -> str:
        try:
            return data.decode('UTF8').strip()
        except ValueError:
            return default
