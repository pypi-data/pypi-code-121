from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureLibraryCreate")


@attr.s(auto_attribs=True, repr=False)
class FeatureLibraryCreate:
    """ Inputs for creating a feature library """

    _organization_id: Union[Unset, str] = UNSET
    _description: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("organization_id={}".format(repr(self._organization_id)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("name={}".format(repr(self._name)))
        return "FeatureLibraryCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        organization_id = self._organization_id
        description = self._description
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if organization_id is not UNSET:
            field_dict["organizationId"] = organization_id
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_organization_id() -> Union[Unset, str]:
            organization_id = d.pop("organizationId")
            return organization_id

        organization_id = get_organization_id() if "organizationId" in d else cast(Union[Unset, str], UNSET)

        def get_description() -> Union[Unset, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        feature_library_create = cls(
            organization_id=organization_id,
            description=description,
            name=name,
        )

        return feature_library_create

    @property
    def organization_id(self) -> str:
        """The organization that will own the feature library. The requesting user must be an administrator of the organization. If unspecified and the organization allows personal ownables, then the requesting user will own the feature library"""
        if isinstance(self._organization_id, Unset):
            raise NotPresentError(self, "organization_id")
        return self._organization_id

    @organization_id.setter
    def organization_id(self, value: str) -> None:
        self._organization_id = value

    @organization_id.deleter
    def organization_id(self) -> None:
        self._organization_id = UNSET

    @property
    def description(self) -> str:
        """ The description for the feature library """
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

    @property
    def name(self) -> str:
        """ The name of the feature library """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
