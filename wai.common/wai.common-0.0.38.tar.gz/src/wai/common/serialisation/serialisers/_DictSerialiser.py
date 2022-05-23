from typing import Dict, Generic, TypeVar, IO

from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser

KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")


class DictSerialiser(
    Serialiser[Dict[KeyType, ValueType]],
    Generic[KeyType, ValueType]
):
    def __init__(
            self,
            key_serialiser: Serialiser[KeyType],
            value_serialiser: Serialiser[ValueType],
            length_serialiser: Serialiser[int] = IntSerialiser(signed=False),
    ):
        super().__init__()

        self._key_serialiser: Serialiser[KeyType] = key_serialiser
        self._value_serialiser: Serialiser[ValueType] = value_serialiser
        self._length_serialiser: Serialiser[int] = length_serialiser

    def _check(
            self,
            obj: Dict[KeyType, ValueType]
    ):
        # Must be a dictionary
        if not isinstance(obj, dict):
            raise ValueError(f"{DictSerialiser.__class__.__name__} serialises dictionaries")

    def _serialise(
            self,
            obj: Dict[KeyType, ValueType],
            stream: IO[bytes]
    ):
        # Serialise the size of the dictionary
        self._length_serialiser.serialise(
            len(obj),
            stream
        )

        # Serialise each key/value pair in turn
        for key, value in obj.items():
            self._key_serialiser.serialise(key, stream)
            self._value_serialiser.serialise(value, stream)

    def _deserialise(
            self,
            stream: IO[bytes]
    ) -> Dict[KeyType, ValueType]:
        # Create a dict to accumulate the key/value pairs as they are deserialised
        result = {}

        # Deserialise the keys and values
        for _ in range(self._length_serialiser.deserialise(stream)):
            key = self._key_serialiser.deserialise(stream)
            value = self._value_serialiser.deserialise(stream)
            result[key] = value

        return result
