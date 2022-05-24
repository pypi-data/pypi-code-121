from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.resource_dependency_types import ResourceDependencyTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="ResourceDependencyLink")


@attr.s(auto_attribs=True, repr=False)
class ResourceDependencyLink:
    """  """

    _type: ResourceDependencyTypes
    _name: str
    _resource_id: Optional[str]
    _api_url: Union[Unset, None, str] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _resource_name: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("resource_id={}".format(repr(self._resource_id)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("resource_name={}".format(repr(self._resource_name)))
        return "ResourceDependencyLink({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        name = self._name
        resource_id = self._resource_id
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

        def get_type() -> ResourceDependencyTypes:
            _type = d.pop("type")
            try:
                type = ResourceDependencyTypes(_type)
            except ValueError:
                type = ResourceDependencyTypes.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(ResourceDependencyTypes, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_resource_id() -> Optional[str]:
            resource_id = d.pop("resourceId")
            return resource_id

        resource_id = get_resource_id() if "resourceId" in d else cast(Optional[str], UNSET)

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

        resource_dependency_link = cls(
            type=type,
            name=name,
            resource_id=resource_id,
            api_url=api_url,
            description=description,
            resource_name=resource_name,
        )

        return resource_dependency_link

    @property
    def type(self) -> ResourceDependencyTypes:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: ResourceDependencyTypes) -> None:
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
