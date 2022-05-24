from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entity_schema_dependency_link_type import EntitySchemaDependencyLinkType
from ..models.schema_dependency_subtypes import SchemaDependencySubtypes
from ..models.subdependency_link import SubdependencyLink
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchemaDependencyLink")


@attr.s(auto_attribs=True, repr=False)
class EntitySchemaDependencyLink:
    """  """

    _type: EntitySchemaDependencyLinkType
    _name: str
    _resource_id: Optional[str]
    _subtype: Union[Unset, SchemaDependencySubtypes] = UNSET
    _field_definitions: Union[Unset, List[SubdependencyLink]] = UNSET
    _api_url: Union[Unset, None, str] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _resource_name: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("resource_id={}".format(repr(self._resource_id)))
        fields.append("subtype={}".format(repr(self._subtype)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("resource_name={}".format(repr(self._resource_name)))
        return "EntitySchemaDependencyLink({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        name = self._name
        resource_id = self._resource_id
        subtype: Union[Unset, int] = UNSET
        if not isinstance(self._subtype, Unset):
            subtype = self._subtype.value

        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        api_url = self._api_url
        description = self._description
        resource_name = self._resource_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "name": name,
                "resourceId": resource_id,
            }
        )
        if subtype is not UNSET:
            field_dict["subtype"] = subtype
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if description is not UNSET:
            field_dict["description"] = description
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> EntitySchemaDependencyLinkType:
            _type = d.pop("type")
            try:
                type = EntitySchemaDependencyLinkType(_type)
            except ValueError:
                type = EntitySchemaDependencyLinkType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(EntitySchemaDependencyLinkType, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_resource_id() -> Optional[str]:
            resource_id = d.pop("resourceId")
            return resource_id

        resource_id = get_resource_id() if "resourceId" in d else cast(Optional[str], UNSET)

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

        def get_field_definitions() -> Union[Unset, List[SubdependencyLink]]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:
                field_definitions_item = SubdependencyLink.from_dict(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(Union[Unset, List[SubdependencyLink]], UNSET)
        )

        def get_api_url() -> Union[Unset, None, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, None, str], UNSET)

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_resource_name() -> Union[Unset, None, str]:
            resource_name = d.pop("resourceName")
            return resource_name

        resource_name = get_resource_name() if "resourceName" in d else cast(Union[Unset, None, str], UNSET)

        entity_schema_dependency_link = cls(
            type=type,
            name=name,
            resource_id=resource_id,
            subtype=subtype,
            field_definitions=field_definitions,
            api_url=api_url,
            description=description,
            resource_name=resource_name,
        )

        return entity_schema_dependency_link

    @property
    def type(self) -> EntitySchemaDependencyLinkType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EntitySchemaDependencyLinkType) -> None:
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
    def resource_id(self) -> Optional[str]:
        if isinstance(self._resource_id, Unset):
            raise NotPresentError(self, "resource_id")
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value: Optional[str]) -> None:
        self._resource_id = value

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
    def field_definitions(self) -> List[SubdependencyLink]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(self, value: List[SubdependencyLink]) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET

    @property
    def api_url(self) -> Optional[str]:
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: Optional[str]) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

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

    @property
    def resource_name(self) -> Optional[str]:
        if isinstance(self._resource_name, Unset):
            raise NotPresentError(self, "resource_name")
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value: Optional[str]) -> None:
        self._resource_name = value

    @resource_name.deleter
    def resource_name(self) -> None:
        self._resource_name = UNSET
