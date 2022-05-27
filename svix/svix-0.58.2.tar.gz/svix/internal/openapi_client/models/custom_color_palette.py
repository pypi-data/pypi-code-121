from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomColorPalette")


@attr.s(auto_attribs=True)
class CustomColorPalette:
    """
    Attributes:
        background_hover (Union[Unset, str]):
        background_primary (Union[Unset, str]):
        background_secondary (Union[Unset, str]):
        interactive_accent (Union[Unset, str]):
        text_danger (Union[Unset, str]):
        text_primary (Union[Unset, str]):
    """

    background_hover: Union[Unset, str] = UNSET
    background_primary: Union[Unset, str] = UNSET
    background_secondary: Union[Unset, str] = UNSET
    interactive_accent: Union[Unset, str] = UNSET
    text_danger: Union[Unset, str] = UNSET
    text_primary: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        background_hover = self.background_hover
        background_primary = self.background_primary
        background_secondary = self.background_secondary
        interactive_accent = self.interactive_accent
        text_danger = self.text_danger
        text_primary = self.text_primary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if background_hover is not UNSET:
            field_dict["backgroundHover"] = background_hover
        if background_primary is not UNSET:
            field_dict["backgroundPrimary"] = background_primary
        if background_secondary is not UNSET:
            field_dict["backgroundSecondary"] = background_secondary
        if interactive_accent is not UNSET:
            field_dict["interactiveAccent"] = interactive_accent
        if text_danger is not UNSET:
            field_dict["textDanger"] = text_danger
        if text_primary is not UNSET:
            field_dict["textPrimary"] = text_primary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        background_hover = dict_copy.pop("backgroundHover", UNSET)

        background_primary = dict_copy.pop("backgroundPrimary", UNSET)

        background_secondary = dict_copy.pop("backgroundSecondary", UNSET)

        interactive_accent = dict_copy.pop("interactiveAccent", UNSET)

        text_danger = dict_copy.pop("textDanger", UNSET)

        text_primary = dict_copy.pop("textPrimary", UNSET)

        custom_color_palette = cls(
            background_hover=background_hover,
            background_primary=background_primary,
            background_secondary=background_secondary,
            interactive_accent=interactive_accent,
            text_danger=text_danger,
            text_primary=text_primary,
        )

        custom_color_palette.additional_properties = dict_copy
        return custom_color_palette

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
