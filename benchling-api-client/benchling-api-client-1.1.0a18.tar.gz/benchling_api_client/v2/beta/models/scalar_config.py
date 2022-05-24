from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.scalar_config_types import ScalarConfigTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScalarConfig")


@attr.s(auto_attribs=True, repr=False)
class ScalarConfig:
    """  """

    _name: str
    _type: ScalarConfigTypes
    _value: Optional[str]
    _description: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("value={}".format(repr(self._value)))
        return "ScalarConfig({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        type = self._type.value

        description = self._description
        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "type": type,
                "value": value,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_type() -> ScalarConfigTypes:
            _type = d.pop("type")
            try:
                type = ScalarConfigTypes(_type)
            except ValueError:
                type = ScalarConfigTypes.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(ScalarConfigTypes, UNSET)

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_value() -> Optional[str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Optional[str], UNSET)

        scalar_config = cls(
            name=name,
            type=type,
            description=description,
            value=value,
        )

        return scalar_config

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> ScalarConfigTypes:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: ScalarConfigTypes) -> None:
        self._type = value

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
    def value(self) -> Optional[str]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._value = value
