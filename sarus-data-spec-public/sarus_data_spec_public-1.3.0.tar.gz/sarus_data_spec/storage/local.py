from collections import defaultdict
from typing import (
    Collection,
    DefaultDict,
    FrozenSet,
    List,
    MutableMapping,
    Optional,
    Set,
    Union,
    cast,
)

from sarus_data_spec.protobuf.typing import (
    ProtobufWithUUID,
    ProtobufWithUUIDAndDatetime,
)
from sarus_data_spec.typing import Referrable, Referring


def referrable_collection_set(
    values: Collection[Referrable[ProtobufWithUUID]],
) -> FrozenSet[str]:
    return frozenset(value.uuid() for value in values)


class Storage:
    """Simple local Storage."""

    def __init__(self) -> None:
        # A Store to save (timestamp, type_name, data, relating data)
        self._referrables: MutableMapping[
            str, Referrable[ProtobufWithUUID]
        ] = dict()
        self._referring: DefaultDict[str, Set[str]] = defaultdict(set)

    def store(self, value: Referrable[ProtobufWithUUID]) -> None:
        # Checks the value for consistency
        assert value._frozen()
        self._referrables[value.uuid()] = value

        if isinstance(value, Referring):
            value = cast(Referring[ProtobufWithUUID], value)
            for referred in value.referred():
                self._referring[referred.uuid()].add(value.uuid())

    def referrable(self, uuid: str) -> Optional[Referrable[ProtobufWithUUID]]:
        return self._referrables.get(uuid, None)

    def referring(
        self,
        referred: Union[
            Referrable[ProtobufWithUUID],
            Collection[Referrable[ProtobufWithUUID]],
        ],
        type_name: Optional[str] = None,
    ) -> Collection[Referring[ProtobufWithUUID]]:
        if not isinstance(referred, Referrable):
            raise NotImplementedError(
                "Local storage does not support referring "
                "with more than one referrable."
            )
        referring_uuids = self._referring[referred.uuid()]
        referrings = [self.referrable(uuid) for uuid in referring_uuids]
        if type_name is not None:
            referrings = [
                item
                for item in referrings
                if (item is not None) and (item.type_name() == type_name)
            ]
        return referrings  # type:ignore

    def last_referring(
        self,
        referred: Union[
            Referrable[ProtobufWithUUID],
            Collection[Referrable[ProtobufWithUUID]],
        ],
        type_name: str,
    ) -> Optional[Referring[ProtobufWithUUIDAndDatetime]]:
        """Last value referring to one referred."""
        raise NotImplementedError()

    def type_name(
        self, type_name: str
    ) -> Collection[Referrable[ProtobufWithUUID]]:
        return {
            ref
            for ref in self._referrables.values()
            if ref.type_name() == type_name
        }

    def all_referrings(self, uuid: str) -> List[str]:
        """Returns a list all items referring to a Referrable recursively."""
        target = self.referrable(uuid)

        to_delete, to_check = set(), {target}
        while len(to_check) > 0:
            node = to_check.pop()
            if not node:
                continue
            to_delete.add(node)
            deps = node.referring()
            if not deps:
                continue
            for dep in deps:
                if dep not in to_delete:
                    to_check.add(dep)

        return [msg.uuid() for msg in to_delete]

    def delete(self, uuid: str) -> None:
        """Delete a Referrable and all elements referring to it to let the
        storage in a consistent state."""
        uuids_to_delete = set(self.all_referrings(uuid))

        self._referrables = {
            k: v
            for k, v in self._referrables.items()
            if k not in uuids_to_delete
        }

        self._referring = defaultdict(
            set,
            {
                k: v - uuids_to_delete
                for k, v in self._referring.items()
                if k not in uuids_to_delete
            },
        )
