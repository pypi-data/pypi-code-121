import inspect
from copy import deepcopy
from pathlib import Path
from typing import Tuple, Any, Dict, List

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loader_manager import LoaderManager
from confident.loaders.default_source_loader import DefaultSourceLoader
from confident.loaders.env_source_loader import EnvSourceLoader
from confident.loaders.file_source_loader import FileSourceLoader
from confident.loaders.init_source_loader import InitSourceLoader
from confident.loaders.map_source_loader import MapSourceLoader
from confident.specs import ConfigSpecs
from confident.utils import get_class_file_path

SPECS_ATTR = '_specs'
LOADER_MANAGER_ATTR = '_loader_manager'


class BaseConfig(BaseSettings):
    __slots__ = (SPECS_ATTR, LOADER_MANAGER_ATTR)

    def __init__(self, **values: Any):
        # Prepare metadata.
        subclass_location = get_class_file_path(cls=self)
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        caller_location = caller_module.__file__ if caller_module else Path.cwd()

        specs = self.Config.__dict__.get('specs')
        if not specs:
            specs_path = values.pop('_specs_path', None) or self.Config.__dict__.get('specs_path')
            if specs_path:
                specs = ConfigSpecs.from_path(
                    path=specs_path, class_path=subclass_location, creation_path=caller_location
                )
            else:
                specs = ConfigSpecs.from_model(
                    model=self, values=values, class_path=subclass_location, creation_path=caller_location
                )

        loader_manager = LoaderManager(settings_obj=self, source_priority=specs.source_priority)
        object.__setattr__(self, SPECS_ATTR, specs)
        object.__setattr__(self, LOADER_MANAGER_ATTR, loader_manager)

        # Create temporary context for the scope of `Config` class.
        self.Config._confident_loader_manager_context_ = loader_manager
        self.Config._confident_specs_context_ = specs

        super().__init__(**values)

        # Reset the context of the Config class, so it will be clean for the next object creation.
        del self.Config._confident_loader_manager_context_
        del self.Config._confident_specs_context_

    def _build_values(self, init_kwargs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        values_dict = super()._build_values(init_kwargs, **kwargs)
        loader_manager = self.__getattribute__(LOADER_MANAGER_ATTR)
        loader_manager.full_fields = values_dict

        return {name: field.value for name, field in values_dict.items()}

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            # Get BaseSettings default loaders callables.
            loader_manager = cls._confident_loader_manager_context_
            specs = cls._confident_specs_context_
            loader_manager.init_settings_callable = init_settings
            loader_manager.env_settings_callable = env_settings
            loader_manager.file_secret_settings_callable = file_secret_settings

            # Add all the default loaders.
            loader_manager.loaders.extend([
                InitSourceLoader(specs=specs, init_settings_callable=init_settings),
                EnvSourceLoader(specs=specs, env_settings_callable=env_settings),
                MapSourceLoader(specs=specs, all_loaded_fields=loader_manager.all_loaded_fields),
                FileSourceLoader(specs=specs),
                DefaultSourceLoader(specs=specs)
            ])

            return loader_manager.load_all()

    @property
    def __specs__(self) -> ConfigSpecs:
        """
        Returns: The model specs.
        """
        return self.__getattribute__(SPECS_ATTR)

    def specs(self):
        return deepcopy(self.__specs__)

    @property
    def __source_priority__(self) -> List[ConfigSource]:
        """
        Returns: List of sources from the highest priority to the lowest.
        """
        return self.__specs__.source_priority

    def source_priority(self):
        return deepcopy(self.__source_priority__)

    @property
    def __full_fields__(self) -> Dict[str, Any]:
        """
        Returns: A dictionary with details of every field.
        """
        return self.__getattribute__(LOADER_MANAGER_ATTR).full_fields

    def full_fields(self):
        return deepcopy(self.__full_fields__)

    @property
    def __all_loaded_fields__(self) -> Dict[str, List[ConfigField]]:
        """
        Returns: A dictionary with all the fields that were loaded before the prioritization classified by sources.
        """
        return self.__getattribute__(LOADER_MANAGER_ATTR).all_loaded_fields

    def all_loaded_fields(self):
        return deepcopy(self.all_loaded_fields)


class Confident(BaseConfig):
    pass
