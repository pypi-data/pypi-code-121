from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record_set import ArchiveRecordSet
from ..models.fields_with_resolution import FieldsWithResolution
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntityBulkUpsertBaseRequest")


@attr.s(auto_attribs=True, repr=False)
class EntityBulkUpsertBaseRequest:
    """  """

    _entity_registry_id: str
    _name: str
    _registry_id: str
    _schema_id: str
    _archive_record: Union[Unset, ArchiveRecordSet] = UNSET
    _fields: Union[Unset, FieldsWithResolution] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntityBulkUpsertBaseRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_registry_id = self._entity_registry_id
        name = self._name
        registry_id = self._registry_id
        schema_id = self._schema_id
        archive_record: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityRegistryId": entity_registry_id,
                "name": name,
                "registryId": registry_id,
                "schemaId": schema_id,
            }
        )
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_registry_id() -> str:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        entity_registry_id = get_entity_registry_id() if "entityRegistryId" in d else cast(str, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_registry_id() -> str:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(str, UNSET)

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_archive_record() -> Union[Unset, ArchiveRecordSet]:
            archive_record: Union[Unset, ArchiveRecordSet] = UNSET
            _archive_record = d.pop("archiveRecord")
            if not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecordSet.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, ArchiveRecordSet], UNSET)
        )

        def get_fields() -> Union[Unset, FieldsWithResolution]:
            fields: Union[Unset, FieldsWithResolution] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = FieldsWithResolution.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, FieldsWithResolution], UNSET)

        entity_bulk_upsert_base_request = cls(
            entity_registry_id=entity_registry_id,
            name=name,
            registry_id=registry_id,
            schema_id=schema_id,
            archive_record=archive_record,
            fields=fields,
        )

        entity_bulk_upsert_base_request.additional_properties = d
        return entity_bulk_upsert_base_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def entity_registry_id(self) -> str:
        """ Registry ID of the entity in Benchling. """
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: str) -> None:
        self._entity_registry_id = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def registry_id(self) -> str:
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @property
    def schema_id(self) -> str:
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def archive_record(self) -> ArchiveRecordSet:
        """ Currently, we only support setting a null value for archiveRecord, which unarchives the item """
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: ArchiveRecordSet) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def fields(self) -> FieldsWithResolution:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: FieldsWithResolution) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET
