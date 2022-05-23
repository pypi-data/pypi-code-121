from typing import IO

from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser


class LengthPrefixedBytesSerialiser(Serialiser[bytes]):
    """
    Serialiser which serialises raw binary data. Inserts the length of
    the data in bytes before the raw binary data.
    """
    def __init__(
            self,
            length_serialiser: Serialiser[int] = IntSerialiser(signed=False)
    ):
        super().__init__()
        self._length_serialiser: Serialiser[int] = length_serialiser

    def _check(self, obj: bytes):
        # All binary data is valid
        pass

    def _serialise(self, obj: bytes, stream: IO[bytes]):
        # Serialise the length of the data
        self._length_serialiser.serialise(len(obj), stream)

        # Write the data
        stream.write(obj)

    def _deserialise(self, stream: IO[bytes]) -> bytes:
        # Read the length from the stream
        byte_length: int = self._length_serialiser.deserialise(stream)

        return stream.read(byte_length)
