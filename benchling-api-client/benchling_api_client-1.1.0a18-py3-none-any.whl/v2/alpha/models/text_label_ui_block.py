from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.text_label_ui_block_type import TextLabelUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TextLabelUiBlock")


@attr.s(auto_attribs=True, repr=False)
class TextLabelUiBlock:
    """  """

    _text: str
    _type: TextLabelUiBlockType

    def __repr__(self):
        fields = []
        fields.append("text={}".format(repr(self._text)))
        fields.append("type={}".format(repr(self._type)))
        return "TextLabelUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        text = self._text
        type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "text": text,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_text() -> str:
            text = d.pop("text")
            return text

        text = get_text() if "text" in d else cast(str, UNSET)

        def get_type() -> TextLabelUiBlockType:
            _type = d.pop("type")
            try:
                type = TextLabelUiBlockType(_type)
            except ValueError:
                type = TextLabelUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(TextLabelUiBlockType, UNSET)

        text_label_ui_block = cls(
            text=text,
            type=type,
        )

        return text_label_ui_block

    @property
    def text(self) -> str:
        if isinstance(self._text, Unset):
            raise NotPresentError(self, "text")
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def type(self) -> TextLabelUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: TextLabelUiBlockType) -> None:
        self._type = value
