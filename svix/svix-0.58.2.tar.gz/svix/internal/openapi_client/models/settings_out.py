from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.custom_color_palette import CustomColorPalette
from ..models.custom_theme_override import CustomThemeOverride
from ..types import UNSET, Unset

T = TypeVar("T", bound="SettingsOut")


@attr.s(auto_attribs=True)
class SettingsOut:
    """
    Attributes:
        color_palette_dark (Union[Unset, CustomColorPalette]):
        color_palette_light (Union[Unset, CustomColorPalette]):
        custom_base_font_size (Union[Unset, int]):
        custom_color (Union[Unset, str]):
        custom_font_family (Union[Unset, str]):  Example: Open Sans.
        custom_logo_url (Union[Unset, str]):
        custom_theme_override (Union[Unset, CustomThemeOverride]):
        disable_endpoint_on_failure (Union[Unset, bool]):  Default: True.
        display_name (Union[Unset, str]):
        enable_channels (Union[Unset, bool]):
        enable_integration_management (Union[Unset, bool]):
        enforce_https (Union[Unset, bool]):  Default: True.
        event_catalog_published (Union[Unset, bool]):
    """

    color_palette_dark: Union[Unset, CustomColorPalette] = UNSET
    color_palette_light: Union[Unset, CustomColorPalette] = UNSET
    custom_base_font_size: Union[Unset, int] = UNSET
    custom_color: Union[Unset, str] = UNSET
    custom_font_family: Union[Unset, str] = UNSET
    custom_logo_url: Union[Unset, str] = UNSET
    custom_theme_override: Union[Unset, CustomThemeOverride] = UNSET
    disable_endpoint_on_failure: Union[Unset, bool] = True
    display_name: Union[Unset, str] = UNSET
    enable_channels: Union[Unset, bool] = False
    enable_integration_management: Union[Unset, bool] = False
    enforce_https: Union[Unset, bool] = True
    event_catalog_published: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        color_palette_dark: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.color_palette_dark, Unset):
            color_palette_dark = self.color_palette_dark.to_dict()

        color_palette_light: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.color_palette_light, Unset):
            color_palette_light = self.color_palette_light.to_dict()

        custom_base_font_size = self.custom_base_font_size
        custom_color = self.custom_color
        custom_font_family = self.custom_font_family
        custom_logo_url = self.custom_logo_url
        custom_theme_override: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.custom_theme_override, Unset):
            custom_theme_override = self.custom_theme_override.to_dict()

        disable_endpoint_on_failure = self.disable_endpoint_on_failure
        display_name = self.display_name
        enable_channels = self.enable_channels
        enable_integration_management = self.enable_integration_management
        enforce_https = self.enforce_https
        event_catalog_published = self.event_catalog_published

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if color_palette_dark is not UNSET:
            field_dict["colorPaletteDark"] = color_palette_dark
        if color_palette_light is not UNSET:
            field_dict["colorPaletteLight"] = color_palette_light
        if custom_base_font_size is not UNSET:
            field_dict["customBaseFontSize"] = custom_base_font_size
        if custom_color is not UNSET:
            field_dict["customColor"] = custom_color
        if custom_font_family is not UNSET:
            field_dict["customFontFamily"] = custom_font_family
        if custom_logo_url is not UNSET:
            field_dict["customLogoUrl"] = custom_logo_url
        if custom_theme_override is not UNSET:
            field_dict["customThemeOverride"] = custom_theme_override
        if disable_endpoint_on_failure is not UNSET:
            field_dict["disableEndpointOnFailure"] = disable_endpoint_on_failure
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if enable_channels is not UNSET:
            field_dict["enableChannels"] = enable_channels
        if enable_integration_management is not UNSET:
            field_dict["enableIntegrationManagement"] = enable_integration_management
        if enforce_https is not UNSET:
            field_dict["enforceHttps"] = enforce_https
        if event_catalog_published is not UNSET:
            field_dict["eventCatalogPublished"] = event_catalog_published

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

        custom_base_font_size = dict_copy.pop("customBaseFontSize", UNSET)

        custom_color = dict_copy.pop("customColor", UNSET)

        custom_font_family = dict_copy.pop("customFontFamily", UNSET)

        custom_logo_url = dict_copy.pop("customLogoUrl", UNSET)

        _custom_theme_override = dict_copy.pop("customThemeOverride", UNSET)
        custom_theme_override: Union[Unset, CustomThemeOverride]
        if isinstance(_custom_theme_override, Unset):
            custom_theme_override = UNSET
        else:
            custom_theme_override = CustomThemeOverride.from_dict(_custom_theme_override)

        disable_endpoint_on_failure = dict_copy.pop("disableEndpointOnFailure", UNSET)

        display_name = dict_copy.pop("displayName", UNSET)

        enable_channels = dict_copy.pop("enableChannels", UNSET)

        enable_integration_management = dict_copy.pop("enableIntegrationManagement", UNSET)

        enforce_https = dict_copy.pop("enforceHttps", UNSET)

        event_catalog_published = dict_copy.pop("eventCatalogPublished", UNSET)

        settings_out = cls(
            color_palette_dark=color_palette_dark,
            color_palette_light=color_palette_light,
            custom_base_font_size=custom_base_font_size,
            custom_color=custom_color,
            custom_font_family=custom_font_family,
            custom_logo_url=custom_logo_url,
            custom_theme_override=custom_theme_override,
            disable_endpoint_on_failure=disable_endpoint_on_failure,
            display_name=display_name,
            enable_channels=enable_channels,
            enable_integration_management=enable_integration_management,
            enforce_https=enforce_https,
            event_catalog_published=event_catalog_published,
        )

        settings_out.additional_properties = dict_copy
        return settings_out

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
