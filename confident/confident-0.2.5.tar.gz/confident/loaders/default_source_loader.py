from typing import List

from pydantic import BaseSettings

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader


class DefaultSourceLoader(SourceLoader):
    NAME = ConfigSource.class_default

    def load_fields(self, settings: BaseSettings) -> List[ConfigField]:
        """
        Loads default values declared in the inheriting class into a dictionary.
        """
        fields = []
        for field_name, model_field in settings.__fields__.items():
            # If the field is required, there is no default value to load.
            if model_field.required:
                continue
            # Uses `pydantic` ModelField to retrieve the default values of the model.
            default_value = model_field.get_default()
            fields.append(ConfigField(
                name=field_name,
                value=default_value,
                source_name=settings.__class__.__name__,
                source_type=ConfigSource.class_default,
                source_location=self.specs.class_path,
            ))
        return fields
