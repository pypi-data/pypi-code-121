from pathlib import Path
from typing import List

from pydantic import BaseSettings

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader
from confident.utils import load_file, convert_field_value


class MapSourceLoader(SourceLoader):
    NAME = ConfigSource.map

    def __init__(self, all_loaded_fields: dict, **kwargs):
        super().__init__(**kwargs)
        self.all_loaded_fields = all_loaded_fields

    def load_fields(self, settings: BaseSettings) -> List[ConfigField]:
        """
        Loads the relevant map config properties.

        Raises:
            ValueError - If wrong combination or values of fields is detected in the following cases:
                If `map_field` and also `map_name` are present.
                If no `config_map` is provided.
                If the `map_name` is not of type `str`.
                If the `map_field` appears inside the `config_map`.
        """
        # Extracts the map metadata field and validates them.
        map_name = self.specs.map_name
        map_field = self.specs.map_field
        config_map = self.specs.config_map
        map_location = self.specs.creation_path

        if map_field is None and map_name is None:
            return []
        if map_field is not None and map_name is not None:
            raise ValueError('Cannot have both `map_field` and `map_name`. Only one can be used.')
        if config_map is None:
            raise ValueError('No `config_map` was provided.')
        if isinstance(config_map, Path):
            map_location = config_map
            config_map = load_file(map_location)

        selected_config = {}
        config_fields = []

        # According to the map name, extracts the chosen config.
        if map_name:
            selected_config = config_map.get(map_name)
        if map_field:
            # Search for the map name in all possible sources ordered by priority.
            for source in self.specs.source_priority:
                if source == ConfigSource.map:
                    continue
                config_property = self.all_loaded_fields[source].get(map_field)
                if config_property:
                    map_name = config_property.value
                    break

            if not isinstance(map_name, str):
                raise ValueError(
                    f'{map_field=} is not valid. Value has to be <str> not "{map_name}" '
                    f'type={type(map_name)}'
                )
            selected_config = config_map.get(map_name)

        if selected_config is None:
            raise KeyError(f'No matching map config to {map_name=}. Check your `config_map`.')

        if isinstance(selected_config, str) or isinstance(selected_config, Path):
            selected_config = load_file(selected_config)

        # Creates the `ConfigField` dictionary.
        for name, value in selected_config.items():
            if name == map_field:
                raise ValueError(
                    f"{map_field=} cannot appear in the map config key '{map_name}'. "
                    f"Look for {map_location=} at '{map_name}'. "
                    f"Remove '{map_field}' key or change the map field."
                )
            config_fields.append(
                ConfigField(
                    name=name,
                    value=convert_field_value(settings=settings, field_name=name, origin_value=value),
                    origin_value=value,
                    source_name=map_name,
                    source_type=ConfigSource.map,
                    source_location=map_location,
                )
            )

        self.specs.map_name = map_name
        return config_fields
