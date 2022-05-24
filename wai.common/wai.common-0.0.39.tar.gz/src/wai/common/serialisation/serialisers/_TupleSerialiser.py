from typing import Generic, TypeVar, IO

from .._Serialiser import Serialiser

TupleType = TypeVar("TupleType", bound=tuple)


class TupleSerialiser(
    Serialiser[TupleType],
    Generic[TupleType]
):
    def __init__(
            self,
            *element_serialisers: Serialiser  # Should be a serialiser matching each element of TupleType,
                                              # but this is not supported yet
    ):
        super().__init__()

        self._element_serialisers = element_serialisers

    def _check(
            self,
            obj: TupleType
    ):
        # Must be a dictionary
        if not isinstance(obj, tuple):
            raise ValueError(f"{TupleSerialiser.__class__.__name__} serialises tuples")

        # Must have the same number of elements as we have element-serialisers
        num_required_elements = len(self._element_serialisers)
        num_received_elements = len(obj)
        if num_received_elements != num_required_elements:
            raise ValueError(f"Expected tuple of {num_required_elements} elements but received {num_received_elements}")

    def _serialise(
            self,
            obj: TupleType,
            stream: IO[bytes]
    ):
        # Serialise each value in turn
        for value, serialiser in zip(obj, self._element_serialisers):
            serialiser.serialise(value, stream)

    def _deserialise(
            self,
            stream: IO[bytes]
    ) -> TupleType:
        # Deserialise the elements in serialised order
        return tuple(
            serialiser.deserialise(stream)
            for serialiser in self._element_serialisers
        )
