"""A few base implementations of basic Protocols
"""
from typing import (
    Collection,
    Mapping,
    MutableSet,
    Optional,
    Type,
    TypeVar,
    cast,
)
from uuid import UUID
import hashlib

from sarus_data_spec.context.typing import Context, HasContext
from sarus_data_spec.manager.typing import HasManager, Manager
from sarus_data_spec.protobuf.typing import Protobuf, ProtobufWithUUID
from sarus_data_spec.protobuf.utilities import copy, json, serialize, type_name
from sarus_data_spec.storage.typing import HasStorage, Storage
import sarus_data_spec.context as sc
import sarus_data_spec.typing as st

P = TypeVar('P', bound=Protobuf, covariant=True)


class Base(st.HasProtobuf[P], st.Value, st.Frozen, HasContext):
    """An object with value semantics, properties, backed by a Protobuf, with
    a default implementation"""

    def __init__(self, protobuf: P) -> None:
        self._protobuf: P = copy(protobuf)
        self._freeze()
        self._context = sc.global_context()

    def protobuf(self) -> P:
        return copy(self._protobuf)

    def prototype(self) -> Type[P]:
        raise NotImplementedError

    def type_name(self) -> str:
        return type_name(self._protobuf)

    def __bytes__(self) -> bytes:
        return serialize(self._protobuf)

    def __repr__(self) -> str:
        return json(self._protobuf)

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, st.Value):
            return bytes(self) == bytes(value)
        else:
            return False

    def __hash__(self) -> int:
        return hash(bytes(self))

    def __getitem__(self, key: str) -> str:
        return cast(str, self._protobuf.properties[key])

    def properties(self) -> Mapping[str, str]:
        return self.protobuf().properties

    def _checksum(self) -> bytes:
        """Compute an md5 checksum"""
        md5 = hashlib.md5()
        md5.update(serialize(self._protobuf))
        return md5.digest()

    def _freeze(self) -> None:
        self._frozen_checksum = self._checksum()

    def _frozen(self) -> bool:
        return self._checksum() == self._frozen_checksum

    def context(self) -> Context:
        return self._context


PU = TypeVar('PU', bound=ProtobufWithUUID, covariant=True)


class Referrable(Base[PU], st.Referrable[PU], HasStorage, HasManager):
    def __init__(self, protobuf: PU) -> None:
        super().__init__(protobuf)
        self._freeze()
        self.storage().store(self)

    def _freeze(self) -> None:
        """Referrable objects keep a uuid consistent with the checksum.
        The checksum is computed with empty uuid
        """
        self._protobuf.uuid = ''
        self._frozen_checksum = self._checksum()
        self._protobuf.uuid = UUID(bytes=self._frozen_checksum).hex

    def _frozen(self) -> bool:
        """The checksum is computed with empty uuid."""
        uuid = self._protobuf.uuid
        self._protobuf.uuid = ''
        result = (self._checksum() == self._frozen_checksum) and (
            uuid == UUID(bytes=self._frozen_checksum).hex
        )
        self._protobuf.uuid = uuid
        return result

    def uuid(self) -> str:
        return self._protobuf.uuid

    def referring(
        self, type_name: Optional[str] = None
    ) -> Collection[st.Referring]:
        return self.storage().referring(self, type_name)

    def storage(self) -> Storage:
        return self.context().storage()

    def manager(self) -> Manager:
        return self.context().manager()


class Referring(Referrable[PU], st.Referring[PU]):
    _referred: MutableSet[str] = set()

    def __init__(self, protobuf: PU) -> None:
        super().__init__(protobuf)

    def referred(self) -> Collection[st.Referrable]:
        result = set()
        for value in self._referred:
            referred = self.storage().referrable(value)
            if referred is not None:
                result.add(referred)
        return result
