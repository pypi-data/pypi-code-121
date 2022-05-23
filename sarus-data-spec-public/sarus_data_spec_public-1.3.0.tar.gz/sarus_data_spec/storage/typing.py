from typing import Collection, Optional, Protocol, Union, runtime_checkable

from sarus_data_spec.protobuf.typing import (
    ProtobufWithUUID,
    ProtobufWithUUIDAndDatetime,
)
from sarus_data_spec.typing import Referrable, Referring

# We want to store objects, be able to filter on their types and keep the last
# added in some type and relating to some object


@runtime_checkable
class Storage(Protocol):
    """Storage protocol
    A Storage can store Referrable and Referring values.
    """

    def store(self, value: Referrable[ProtobufWithUUID]) -> None:
        """Write a value to store."""
        ...

    def referrable(self, uuid: str) -> Optional[Referrable[ProtobufWithUUID]]:
        """Read a stored value."""
        ...

    def referring(
        self,
        referred: Union[
            Referrable[ProtobufWithUUID],
            Collection[Referrable[ProtobufWithUUID]],
        ],
        type_name: Optional[str] = None,
    ) -> Collection[Referring[ProtobufWithUUID]]:
        """List all values referring to one referred."""
        ...

    def last_referring(
        self,
        referred: Union[
            Referrable[ProtobufWithUUID],
            Collection[Referrable[ProtobufWithUUID]],
        ],
        type_name: str,
    ) -> Optional[Referring[ProtobufWithUUIDAndDatetime]]:
        """Last value referring to one referred."""
        ...

    def type_name(
        self, type_name: str
    ) -> Collection[Referrable[ProtobufWithUUID]]:
        """List all values from a given type_name."""
        ...

    def delete(self, uuid: str) -> None:
        """Delete a stored value from the database."""
        ...


@runtime_checkable
class HasStorage(Protocol):
    """Has a storage for persistent objects."""

    def storage(self) -> Storage:
        """Return a storage (usually a singleton)."""
        ...
