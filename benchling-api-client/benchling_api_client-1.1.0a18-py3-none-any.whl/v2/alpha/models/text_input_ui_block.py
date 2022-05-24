from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.text_input_ui_block_type import TextInputUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TextInputUiBlock")


@attr.s(auto_attribs=True, repr=False)
class TextInputUiBlock:
    """  """

    _type: TextInputUiBlockType
    _id: str
    _placeholder: Union[Unset, None, str] = UNSET
    _value: Union[Unset, None, str] = UNSET
    _enabled: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("placeholder={}".format(repr(self._placeholder)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("enabled={}".format(repr(self._enabled)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TextInputUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        id = self._id
        placeholder = self._placeholder
        value = self._value
        enabled = self._enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "id": id,
            }
        )
        if placeholder is not UNSET:
            field_dict["placeholder"] = placeholder
        if value is not UNSET:
            field_dict["value"] = value
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> TextInputUiBlockType:
            _type = d.pop("type")
            try:
                type = TextInputUiBlockType(_type)
            except ValueError:
                type = TextInputUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(TextInputUiBlockType, UNSET)

        def get_id() -> str:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(str, UNSET)

        def get_placeholder() -> Union[Unset, None, str]:
            placeholder = d.pop("placeholder")
            return placeholder

        placeholder = get_placeholder() if "placeholder" in d else cast(Union[Unset, None, str], UNSET)

        def get_value() -> Union[Unset, None, str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, None, str], UNSET)

        def get_enabled() -> Union[Unset, None, bool]:
            enabled = d.pop("enabled")
            return enabled

        enabled = get_enabled() if "enabled" in d else cast(Union[Unset, None, bool], UNSET)

        text_input_ui_block = cls(
            type=type,
            id=id,
            placeholder=placeholder,
            value=value,
            enabled=enabled,
        )

        text_input_ui_block.additional_properties = d
        return text_input_ui_block

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
    def type(self) -> TextInputUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: TextInputUiBlockType) -> None:
        self._type = value

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def placeholder(self) -> Optional[str]:
        if isinstance(self._placeholder, Unset):
            raise NotPresentError(self, "placeholder")
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        self._placeholder = value

    @placeholder.deleter
    def placeholder(self) -> None:
        self._placeholder = UNSET

    @property
    def value(self) -> Optional[str]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET

    @property
    def enabled(self) -> Optional[bool]:
        if isinstance(self._enabled, Unset):
            raise NotPresentError(self, "enabled")
        return self._enabled

    @enabled.setter
    def enabled(self, value: Optional[bool]) -> None:
        self._enabled = value

    @enabled.deleter
    def enabled(self) -> None:
        self._enabled = UNSET
