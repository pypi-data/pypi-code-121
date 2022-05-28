import os
from typing import List

from pydantic import BaseSettings

from confident.config_field import ConfigField
from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader
from confident.utils import load_file, convert_field_value


class FileSourceLoader(SourceLoader):
    NAME = ConfigSource.file

    def load_fields(self, settings: BaseSettings) -> List[ConfigField]:
        """
        Finds and loads requested config fields from files into a dictionary.

        Raises:
            ValueError -
                If file is not exists and ignore_missing_files=False.
                If the file is not in a supported format.
        """
        fields = {}
        for file_path in self.specs.files:
            if not os.path.isfile(file_path) and self.specs.ignore_missing_files:
                continue
            file_dict = load_file(path=file_path)

            # Creates a dict with `ConfigField` from the file data and merges them with the rest of the properties
            # from other files.
            fields.update(
                {key: ConfigField(
                    name=key,
                    value=convert_field_value(settings=settings, field_name=key, origin_value=value),
                    origin_value=value,
                    source_name=os.path.basename(file_path),
                    source_type=ConfigSource.file,
                    source_location=file_path
                ) for key, value in file_dict.items()})

        # Returns only the properties that are relevant to the class definition.
        return [fields[key] for key in fields.keys() & settings.__fields__.keys()]

