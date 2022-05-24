from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.markdown_ui_block_type import MarkdownUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MarkdownUiBlock")


@attr.s(auto_attribs=True, repr=False)
class MarkdownUiBlock:
    """  """

    _type: MarkdownUiBlockType
    _value: str

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("value={}".format(repr(self._value)))
        return "MarkdownUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> MarkdownUiBlockType:
            _type = d.pop("type")
            try:
                type = MarkdownUiBlockType(_type)
            except ValueError:
                type = MarkdownUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(MarkdownUiBlockType, UNSET)

        def get_value() -> str:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(str, UNSET)

        markdown_ui_block = cls(
            type=type,
            value=value,
        )

        return markdown_ui_block

    @property
    def type(self) -> MarkdownUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: MarkdownUiBlockType) -> None:
        self._type = value

    @property
    def value(self) -> str:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value
