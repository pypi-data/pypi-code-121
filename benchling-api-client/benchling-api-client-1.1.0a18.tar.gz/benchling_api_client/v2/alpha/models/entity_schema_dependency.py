from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.base_manifest_config import BaseManifestConfig
from ..models.entity_schema_dependency_type import EntitySchemaDependencyType
from ..models.schema_dependency_subtypes import SchemaDependencySubtypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchemaDependency")


@attr.s(auto_attribs=True, repr=False)
class EntitySchemaDependency:
    """  """

    _type: EntitySchemaDependencyType
    _name: str
    _subtype: Union[Unset, SchemaDependencySubtypes] = UNSET
    _field_definitions: Union[Unset, List[BaseManifestConfig]] = UNSET
    _description: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("subtype={}".format(repr(self._subtype)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("description={}".format(repr(self._description)))
        return "EntitySchemaDependency({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        name = self._name
        subtype: Union[Unset, int] = UNSET
        if not isinstance(self._subtype, Unset):
            subtype = self._subtype.value

        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        description = self._description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "name": name,
            }
        )
        if subtype is not UNSET:
            field_dict["subtype"] = subtype
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> EntitySchemaDependencyType:
            _type = d.pop("type")
            try:
                type = EntitySchemaDependencyType(_type)
            except ValueError:
                type = EntitySchemaDependencyType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(EntitySchemaDependencyType, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_subtype() -> Union[Unset, SchemaDependencySubtypes]:
            subtype = None
            _subtype = d.pop("subtype")
            if _subtype is not None and _subtype is not UNSET:
                try:
                    subtype = SchemaDependencySubtypes(_subtype)
                except ValueError:
                    subtype = SchemaDependencySubtypes.of_unknown(_subtype)

            return subtype

        subtype = get_subtype() if "subtype" in d else cast(Union[Unset, SchemaDependencySubtypes], UNSET)

        def get_field_definitions() -> Union[Unset, List[BaseManifestConfig]]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:
                field_definitions_item = BaseManifestConfig.from_dict(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(Union[Unset, List[BaseManifestConfig]], UNSET)
        )

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        entity_schema_dependency = cls(
            type=type,
            name=name,
            subtype=subtype,
            field_definitions=field_definitions,
            description=description,
        )

        return entity_schema_dependency

    @property
    def type(self) -> EntitySchemaDependencyType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EntitySchemaDependencyType) -> None:
        self._type = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def subtype(self) -> SchemaDependencySubtypes:
        if isinstance(self._subtype, Unset):
            raise NotPresentError(self, "subtype")
        return self._subtype

    @subtype.setter
    def subtype(self, value: SchemaDependencySubtypes) -> None:
        self._subtype = value

    @subtype.deleter
    def subtype(self) -> None:
        self._subtype = UNSET

    @property
    def field_definitions(self) -> List[BaseManifestConfig]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(self, value: List[BaseManifestConfig]) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET

    @property
    def description(self) -> Optional[str]:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET
