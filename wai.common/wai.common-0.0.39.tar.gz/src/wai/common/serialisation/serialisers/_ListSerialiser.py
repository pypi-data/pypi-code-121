from typing import List, Generic, TypeVar, IO

from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser

ElementType = TypeVar("ElementType")


class ListSerialiser(
    Serialiser[List[ElementType]],
    Generic[ElementType]
):
    def __init__(
            self,
            element_serialiser: Serialiser[ElementType],
            length_serialiser: Serialiser[int] = IntSerialiser(signed=False)
    ):
        super().__init__()

        self._element_serialiser = element_serialiser
        self._length_serialiser = length_serialiser

    def _check(
            self,
            obj: List[ElementType]
    ):
        # Must be a list
        if not isinstance(obj, list):
            raise ValueError(f"{ListSerialiser.__class__.__name__} serialises lists")

    def _serialise(
            self,
            obj: List[ElementType],
            stream: IO[bytes]
    ):
        # Serialise the length of the list
        self._length_serialiser.serialise(len(obj), stream)

        # Serialise each value in turn
        for value in obj:
            self._element_serialiser.serialise(value, stream)

    def _deserialise(
            self,
            stream: IO[bytes]
    ) -> List[ElementType]:
        # Deserialise the length of the list
        length = self._length_serialiser.deserialise(stream)

        # Deserialise 'length' number of elements in serialised order
        return [
            self._element_serialiser.deserialise(stream)
            for _index in range(length)
        ]
