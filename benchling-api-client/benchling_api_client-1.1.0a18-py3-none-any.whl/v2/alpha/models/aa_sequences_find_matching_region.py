from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequencesFindMatchingRegion")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesFindMatchingRegion:
    """  """

    _container_sequence_ids: List[str]
    _schema_id: str
    _registry_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("container_sequence_ids={}".format(repr(self._container_sequence_ids)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        return "AaSequencesFindMatchingRegion({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_sequence_ids = self._container_sequence_ids

        schema_id = self._schema_id
        registry_id = self._registry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerSequenceIds": container_sequence_ids,
                "schemaId": schema_id,
            }
        )
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_sequence_ids() -> List[str]:
            container_sequence_ids = cast(List[str], d.pop("containerSequenceIds"))

            return container_sequence_ids

        container_sequence_ids = (
            get_container_sequence_ids() if "containerSequenceIds" in d else cast(List[str], UNSET)
        )

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_registry_id() -> Union[Unset, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, str], UNSET)

        aa_sequences_find_matching_region = cls(
            container_sequence_ids=container_sequence_ids,
            schema_id=schema_id,
            registry_id=registry_id,
        )

        return aa_sequences_find_matching_region

    @property
    def container_sequence_ids(self) -> List[str]:
        """ API ID of the AA which matching regions will be found for """
        if isinstance(self._container_sequence_ids, Unset):
            raise NotPresentError(self, "container_sequence_ids")
        return self._container_sequence_ids

    @container_sequence_ids.setter
    def container_sequence_ids(self, value: List[str]) -> None:
        self._container_sequence_ids = value

    @property
    def schema_id(self) -> str:
        """ Schema ID for the type of AA to match to the source sequence """
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def registry_id(self) -> str:
        """ An optional Registry ID to restrict the region search to """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET
