from __future__ import annotations
import re
from copy import copy
import os
import json
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, Callable, Type, Sequence, TypeVar
from flask import app

from flask_sqlalchemy import SQLAlchemy
from warepy import get_enum_values, log, format_message, join_paths, load_yaml

from puft.constants.enums import AppModeEnum, ConfigExtensionEnum
from puft.constants.orm_types import Model
from puft.errors.error import Error

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports
    # and use just for typehints.
    from ..services.puft import Puft
    from ..services.database import Database
    from ...views.view import View
    from ...emitters.emitter import Emitter
    from ..mappers.mapper import Mapper
    from ..services.service import Service
    from ...constants.hints import CLIModeEnumUnion


# Set TypeVar upper bound to class defined afterwards.
# https://stackoverflow.com/a/67662276
AnyNamedCell = TypeVar("AnyNamedCell", bound="NamedCell")


@dataclass
class Cell:
    pass


@dataclass
class NamedCell(Cell):
    name: str

    @staticmethod
    def find_by_name(name: str, cells: Sequence[AnyNamedCell]) -> AnyNamedCell:
        """Traverse through given list of cells and return first one with
        specified name.
        
        Raise:
            ValueError: 
                No cell with given name found.
        """
        for cell in cells:
            if cell.name == name:
                return cell
        raise ValueError(
            format_message("No cell with given name {} found.", name))

    @staticmethod
    def map_to_name(cells: list[AnyNamedCell]) -> dict[str, AnyNamedCell]:
        """Traverse through given cells names and return dict with these cells
        as values and their names as keys."""
        cells_by_name: dict[str, AnyNamedCell] = {}
        for cell in cells:
            cells_by_name[cell.name] = cell
        return cells_by_name


@dataclass
class ConfigCell(NamedCell):
    """Config cell which can be used to load configs to appropriate instance's
    configuration by name."""
    source_by_app_mode: dict[AppModeEnum, str]

    def parse(
            self, app_mode_enum: AppModeEnum, root_path: str,
            update_with: dict[str, Any] | None = None,
            convert_keys_to_lower: bool = True) -> dict[str, Any]:
        """Parse config cell and return configuration dictionary.

        Args:
            app_mode_enum:
                App mode to run appropriate config.
            root_path:
                Path to join config cell source with.
            update_with (optional):
                Dictionary to update config cell mapping with.
                Defaults to None.
            convert_keys_to_lower (optional):
                If true, all keys from origin mapping and mapping from
                `update_with` will be converted to upper case.
        
        Raise:
            ValueError:
                If given config cell's source has unrecognized extension.
        """
        res_config: dict[str, Any] = {}

        config_by_mode: dict[AppModeEnum, dict] = self._load_config_by_mode()
        res_config = self._update_config_for_mode(config_by_mode, app_mode_enum)

        if res_config:
            self._parse_string_config_values(res_config, root_path)
        else:
            res_config = {}

        # Update given config with extra dictionary if this dictionary given
        # and not empty.
        if update_with:
            res_config.update(update_with)

        if convert_keys_to_lower:
            temp_config = {}
            for k, v in res_config.items():
                temp_config[k.lower()] = v
            res_config = temp_config

        return res_config

    def _update_config_for_mode(
            self,
            config_by_mode: dict[AppModeEnum, dict],
            app_mode_enum: AppModeEnum) -> dict:
        """Take config maps for each mode and return result config updated for
        current mode.
        
        E.g., given mode is TEST, so final config will be PROD config updated
        by DEV config and then updated by TEST config (so test keys will
        take priority).
        """ 
        prod_config = copy(config_by_mode[AppModeEnum.PROD])

        if app_mode_enum is AppModeEnum.TEST:
            dev_config = copy(config_by_mode[AppModeEnum.DEV])
            test_config = copy(config_by_mode[AppModeEnum.TEST])
            dev_config.update(test_config)
            prod_config.update(dev_config)
        elif app_mode_enum is AppModeEnum.DEV:
            dev_config = copy(config_by_mode[AppModeEnum.DEV])
            prod_config.update(dev_config)
        else:
            # Prod mode, do nothing extra.
            pass
        return prod_config
    
    def _load_config_by_mode(self) -> dict[AppModeEnum, dict]:
        config_by_mode: dict[AppModeEnum, dict] = {}
        for app_mode_enum in AppModeEnum:
            try:
                source = self.source_by_app_mode[app_mode_enum]
            except KeyError:
                # No source for such mode.
                config_by_mode[app_mode_enum] = {}
                continue
            source_extension = source[source.rfind(".")+1:]
            config_by_mode[app_mode_enum] = self._load_config_from_file(
                source_extension_enum=ConfigExtensionEnum(source_extension),
                source=source)
        return config_by_mode
    
    def _load_config_from_file(
            self,
            source_extension_enum: ConfigExtensionEnum, source: str) -> dict:
        # Fetch extension and load config from file.
        match source_extension_enum:
            case ConfigExtensionEnum.JSON:
                with open(source, "r") as config_file:
                    config = json.load(config_file)
            case ConfigExtensionEnum.YAML:
                config = load_yaml(source)
            case _:
                error_message = format_message(
                    "Unrecognized config cell source's extension.")
                raise ValueError(error_message)
        return config
    
    def _parse_string_config_values(
            self, config: dict[str, Any], root_path: str) -> None:
        for k, v in config.items():
            if type(v) == str:
                # Find environs to be requested.
                # Exclude escaped curly braces like `\{not_environ\}`.
                envs: list[str] = re.findall(r"[^\\]\{\w+\}", v)
                if envs:
                    for env in [
                                x.replace("{", "").replace("}", "")
                                for x in envs
                            ]:
                        env = env.strip()
                        real_env_value = os.getenv(env.strip())
                        if real_env_value is None:
                            raise ValueError(
                                f"Environ {env} specified in field"
                                f" {self.name}.{k} was not found")
                        else:
                            v = v.replace("{" + f"{env}" + "}", real_env_value)

                # Look for escaped curly braces and normalize them.
                v = v.replace(r"\{", "{").replace(r"\}", "}")

                # Find paths required to be joined to the root path.
                if v[0] == "." and v[1] == "/":
                    config[k] = join_paths(root_path, v)
                else:
                    config[k] = v


@dataclass
class ServiceCell(NamedCell):
    service_class: type[Service]


@dataclass
class PuftServiceCell(ServiceCell):
    """Injection cell with app itself which is required in any build."""
    service_class: type[Puft]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int
    ctx_processor_func: Callable | None = None
    each_request_func: Callable | None = None
    first_request_func: Callable | None = None


@dataclass
class DatabaseServiceCell(ServiceCell):
    """Injection cell with database itself which can be applied to created application."""
    service_class: Type[Database]


@dataclass
class MapperCell(Cell):
    mapper_class: type[Mapper]
    model: type[Model]


@dataclass
class ViewCell(Cell):
    endpoint: str
    view_class: type[View]
    route: str  # Route will be the same for all methods.


@dataclass
class EmitterCell(Cell):
    emitter_class: type[Emitter]


@dataclass
class ErrorCell(Cell):
    error_class: type[Error]
    handler_function: Callable
