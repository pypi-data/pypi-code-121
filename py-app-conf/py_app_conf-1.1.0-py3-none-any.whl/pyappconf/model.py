import json
import os
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, Union

import appdirs
import toml
import yaml
from pydantic import BaseModel, BaseSettings, validator
from pydantic.env_settings import EnvSettingsSource
from pydantic.fields import ModelField
from pydantic.schema import default_ref_template
from toml.encoder import TomlEncoder

from pyappconf.encoding.ext_json import ExtendedJSONEncoder
from pyappconf.encoding.ext_toml import CustomTomlEncoder
from pyappconf.encoding.ext_yaml import CustomDumper


def _output_if_necessary(content: str, out_path: Optional[Union[str, Path]] = None):
    if out_path is not None:
        out_path = Path(out_path)
        out_path.write_text(content)


def _get_data_kwargs(**kwargs):
    default_kwargs = dict(
        exclude={"settings"},
    )
    if "exclude" in kwargs:
        default_kwargs["exclude"].update(kwargs["exclude"])
    kwargs.update(default_kwargs)
    return kwargs


class ConfigFormats(str, Enum):
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"

    @classmethod
    def from_path(cls, path: Path) -> "ConfigFormats":
        ext = path.suffix.strip(".").casefold()
        if ext in ("yml", "yaml"):
            return cls.YAML
        if ext == "json":
            return cls.JSON
        if ext == "toml":
            return cls.TOML
        raise ValueError(
            f"suffix {ext} not a supported config format. Supplied path: {path}"
        )


class AppConfig:
    def __init__(
        self,
        app_name: str,
        config_name: str = "config",
        custom_config_folder: Optional[Path] = None,
        default_format: ConfigFormats = ConfigFormats.TOML,
        schema_url: Optional[str] = None,
        toml_encoder: Type[TomlEncoder] = CustomTomlEncoder,
        yaml_encoder: Type = CustomDumper,
        json_encoder: Type[json.JSONEncoder] = ExtendedJSONEncoder,
    ):
        self.app_name = app_name
        self.config_name = config_name
        self.custom_config_folder = custom_config_folder
        self.default_format = default_format
        self.schema_url = schema_url
        self.toml_encoder = toml_encoder
        self.yaml_encoder = yaml_encoder
        self.json_encoder = json_encoder

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema[
            "description"
        ] = "Please ignore this field. It is used for internal purposes."

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def dict(self) -> Dict[str, Any]:
        return self.__dict__

    def copy(self, **kwargs) -> "AppConfig":
        if not kwargs:
            return deepcopy(self)
        config_data = self.dict()
        return self.__class__(**{**config_data, **kwargs})

    @property
    def config_base_location(self) -> Path:
        if self.custom_config_folder is not None:
            return self.custom_config_folder / self.config_name
        return Path(appdirs.user_config_dir(self.app_name)) / self.config_name

    @property
    def config_location(self) -> Path:
        return Path(str(self.config_base_location) + "." + self.default_format.value)

    @property
    def config_file_name(self) -> str:
        return self.config_location.name


class BaseConfig(BaseSettings):
    _settings: AppConfig
    settings: AppConfig = None  # type: ignore

    @validator("settings")
    def set_settings_from_class_if_none(cls, v):
        if v is None:
            return cls._settings.copy()
        return v

    def get_serializer(
        self,
    ) -> Callable[[Optional[Union[str, Path]], Optional[Dict[str, Any]]], str]:
        if self.settings.default_format == ConfigFormats.TOML:
            return self.to_toml
        if self.settings.default_format == ConfigFormats.YAML:
            return self.to_yaml
        if self.settings.default_format == ConfigFormats.JSON:
            return self.to_json
        raise NotImplementedError(f"unsupported format {self.settings.default_format}")

    @classmethod
    def get_deserializer(
        cls, config_format: Optional[ConfigFormats] = None
    ) -> Callable[[Union[str, Path]], "BaseConfig"]:
        if config_format is None:
            config_format = cls._settings.default_format

        if config_format == ConfigFormats.TOML:
            return cls.parse_toml
        if config_format == ConfigFormats.YAML:
            return cls.parse_yaml
        if config_format == ConfigFormats.JSON:
            return cls.parse_json
        raise NotImplementedError(f"unsupported format {config_format}")

    @classmethod
    def _settings_with_overrides(cls, **kwargs) -> AppConfig:
        return cls._settings.copy(**kwargs)

    def save(self, serializer_kwargs: Optional[Dict[str, Any]] = None, **kwargs):
        if not self.settings.config_location.parent.exists():
            self.settings.config_location.parent.mkdir(parents=True)
        self.get_serializer()(self.settings.config_location, serializer_kwargs, **kwargs)  # type: ignore

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> "BaseConfig":
        assign_settings = True

        config_format: Optional[ConfigFormats]
        if path is None:
            assign_settings = False
            path = cls._settings.config_location
            config_format = None
        else:
            path = Path(path)
            config_format = ConfigFormats.from_path(path)

        obj = cls.get_deserializer(config_format)(path)
        if assign_settings:
            obj.settings = cls._settings_with_overrides(
                custom_config_folder=path.parent,
                default_format=config_format,
                config_name=path.stem,
            )
        return obj

    @classmethod
    def load_or_create(cls, path: Optional[Union[str, Path]] = None) -> "BaseConfig":
        if path is None:
            path = cls._settings.config_location
        else:
            path = Path(path)
        if path.exists():
            return cls.load(path)
        else:
            config_format = ConfigFormats.from_path(path)
            return cls(
                settings=cls._settings_with_overrides(
                    custom_config_folder=path.parent,
                    default_format=config_format,
                    config_name=path.stem,
                )
            )

    @classmethod
    def load_recursive(cls, path: Optional[Union[str, Path]] = None) -> "BaseConfig":
        """
        Searches the passed path or current directory for a config with the correct name,
        and if not found goes the parent directory and repeats the search.
        If the config is not found after reaching the root directory,
        it will look at the location in the config.

        :param path: The path to start searching from, defaults to the current directory
        :return:
        """
        path = Path(path or os.getcwd()).absolute()
        current_path = path

        def has_hit_root_directory() -> bool:
            return current_path.parent == current_path

        file_name = cls._settings.config_file_name
        while True:
            check_path = current_path / file_name
            if check_path.exists():
                return cls.load(check_path)
            if has_hit_root_directory():
                break
            current_path = current_path.parent

        # Could not find config after reaching root directory. Try
        # loading from default location
        return cls.load()

    @classmethod
    def _get_env_values(cls) -> Dict[str, Any]:
        env_file = getattr(cls.Config, "env_file", None)
        source = EnvSettingsSource(env_file=env_file, env_file_encoding=None)
        return source(cls)  # type: ignore

    def to_yaml(
        self,
        out_path: Optional[Union[str, Path]] = None,
        yaml_kwargs: Optional[Dict[str, Any]] = None,
        include_schema_url: bool = True,
        **kwargs,
    ) -> str:
        if yaml_kwargs is None:
            yaml_kwargs = {}
        kwargs = _get_data_kwargs(**kwargs)
        data = self.dict(**kwargs)
        yaml_str = yaml.dump(data, **yaml_kwargs, Dumper=self.settings.yaml_encoder)
        if include_schema_url and self.settings.schema_url is not None:
            yaml_str = f"# yaml-language-server: $schema={self.settings.schema_url}\n{yaml_str}"
        _output_if_necessary(yaml_str, out_path)
        return yaml_str

    @classmethod
    def parse_yaml(cls, in_path: Union[str, Path]) -> "BaseConfig":
        data = yaml.safe_load(Path(in_path).read_text())
        data.update(cls._get_env_values())
        return cls(**data)

    def to_toml(
        self,
        out_path: Optional[Union[str, Path]] = None,
        toml_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        if toml_kwargs is None:
            toml_kwargs = {}
        kwargs = _get_data_kwargs(**kwargs)
        data = self.dict(**kwargs)
        toml_str = toml.dumps(data, **toml_kwargs, encoder=self.settings.toml_encoder())  # type: ignore
        # TODO: Add schema URL to TOML once there is a specification for it
        _output_if_necessary(toml_str, out_path)
        return toml_str

    @classmethod
    def parse_toml(cls, in_path: Union[str, Path]) -> "BaseConfig":
        data = toml.load(in_path)
        data.update(cls._get_env_values())
        return cls(**data)

    def to_json(
        self,
        out_path: Optional[Union[str, Path]] = None,
        json_kwargs: Optional[Dict[str, Any]] = None,
        include_schema_url: bool = True,
        **kwargs,
    ) -> str:
        if json_kwargs is None:
            json_kwargs = {}
        if "indent" not in json_kwargs:
            json_kwargs["indent"] = 2
        kwargs = _get_data_kwargs(**kwargs)
        data = self.dict(**kwargs)
        if include_schema_url and self.settings.schema_url is not None:
            data["$schema"] = self.settings.schema_url
        json_str = json.dumps(data, **json_kwargs, cls=self.settings.json_encoder)
        _output_if_necessary(json_str, out_path)
        return json_str

    @classmethod
    def parse_json(cls, in_path: Union[str, Path]) -> "BaseConfig":
        data = json.loads(Path(in_path).read_text())
        data.update(cls._get_env_values())
        if "$schema" in data:
            # Schema is not kept in instance data, it is in cls._settings.schema_url
            del data["$schema"]
        return cls(**data)

    @classmethod
    def schema(
        cls, by_alias: bool = True, ref_template: str = default_ref_template
    ) -> Dict[str, Any]:
        schema = super().schema(by_alias=by_alias, ref_template=ref_template)
        if "properties" in schema and "settings" in schema["properties"]:
            del schema["properties"]["settings"]
        return schema
