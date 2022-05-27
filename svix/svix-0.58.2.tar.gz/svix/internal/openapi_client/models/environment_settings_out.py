from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.custom_color_palette import CustomColorPalette
from ..models.custom_theme_override import CustomThemeOverride
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentSettingsOut")


@attr.s(auto_attribs=True)
class EnvironmentSettingsOut:
    """
    Attributes:
        color_palette_dark (Union[Unset, CustomColorPalette]):
        color_palette_light (Union[Unset, CustomColorPalette]):
        custom_color (Union[Unset, str]):
        custom_font_family (Union[Unset, str]):  Example: Open Sans.
        custom_logo_url (Union[Unset, str]):
        custom_theme_override (Union[Unset, CustomThemeOverride]):
        enable_channels (Union[Unset, bool]):
        enable_integration_management (Union[Unset, bool]):
    """

    color_palette_dark: Union[Unset, CustomColorPalette] = UNSET
    color_palette_light: Union[Unset, CustomColorPalette] = UNSET
    custom_color: Union[Unset, str] = UNSET
    custom_font_family: Union[Unset, str] = UNSET
    custom_logo_url: Union[Unset, str] = UNSET
    custom_theme_override: Union[Unset, CustomThemeOverride] = UNSET
    enable_channels: Union[Unset, bool] = False
    enable_integration_management: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        color_palette_dark: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.color_palette_dark, Unset):
            color_palette_dark = self.color_palette_dark.to_dict()

        color_palette_light: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.color_palette_light, Unset):
            color_palette_light = self.color_palette_light.to_dict()

        custom_color = self.custom_color
        custom_font_family = self.custom_font_family
        custom_logo_url = self.custom_logo_url
        custom_theme_override: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.custom_theme_override, Unset):
            custom_theme_override = self.custom_theme_override.to_dict()

        enable_channels = self.enable_channels
        enable_integration_management = self.enable_integration_management

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if color_palette_dark is not UNSET:
            field_dict["colorPaletteDark"] = color_palette_dark
        if color_palette_light is not UNSET:
            field_dict["colorPaletteLight"] = color_palette_light
        if custom_color is not UNSET:
            field_dict["customColor"] = custom_color
        if custom_font_family is not UNSET:
            field_dict["customFontFamily"] = custom_font_family
        if custom_logo_url is not UNSET:
            field_dict["customLogoUrl"] = custom_logo_url
        if custom_theme_override is not UNSET:
            field_dict["customThemeOverride"] = custom_theme_override
        if enable_channels is not UNSET:
            field_dict["enableChannels"] = enable_channels
        if enable_integration_management is not UNSET:
            field_dict["enableIntegrationManagement"] = enable_integration_management

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        _color_palette_dark = dict_copy.pop("colorPaletteDark", UNSET)
        color_palette_dark: Union[Unset, CustomColorPalette]
        if isinstance(_color_palette_dark, Unset):
            color_palette_dark = UNSET
        else:
            color_palette_dark = CustomColorPalette.from_dict(_color_palette_dark)

        _color_palette_light = dict_copy.pop("colorPaletteLight", UNSET)
        color_palette_light: Union[Unset, CustomColorPalette]
        if isinstance(_color_palette_light, Unset):
            color_palette_light = UNSET
        else:
            color_palette_light = CustomColorPalette.from_dict(_color_palette_light)

        custom_color = dict_copy.pop("customColor", UNSET)

        custom_font_family = dict_copy.pop("customFontFamily", UNSET)

        custom_logo_url = dict_copy.pop("customLogoUrl", UNSET)

        _custom_theme_override = dict_copy.pop("customThemeOverride", UNSET)
        custom_theme_override: Union[Unset, CustomThemeOverride]
        if isinstance(_custom_theme_override, Unset):
            custom_theme_override = UNSET
        else:
            custom_theme_override = CustomThemeOverride.from_dict(_custom_theme_override)

        enable_channels = dict_copy.pop("enableChannels", UNSET)

        enable_integration_management = dict_copy.pop("enableIntegrationManagement", UNSET)

        environment_settings_out = cls(
            color_palette_dark=color_palette_dark,
            color_palette_light=color_palette_light,
            custom_color=custom_color,
            custom_font_family=custom_font_family,
            custom_logo_url=custom_logo_url,
            custom_theme_override=custom_theme_override,
            enable_channels=enable_channels,
            enable_integration_management=enable_integration_management,
        )

        environment_settings_out.additional_properties = dict_copy
        return environment_settings_out

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
