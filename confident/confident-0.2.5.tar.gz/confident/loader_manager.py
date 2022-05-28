from typing import Optional, Callable, List

from confident.config_source import ConfigSource
from confident.loaders.source_loader_base import SourceLoader


class LoaderManager:
    def __init__(
            self,
            settings_obj: object,
            source_priority: List[str],
            init_settings_callable: Optional[Callable] = None,
            env_settings_callable: Optional[Callable] = None,
            file_secret_settings_callable: Optional[Callable] = None,
            loaders: Optional[List[SourceLoader]] = None,
    ):
        self.settings_obj = settings_obj
        self.init_settings_callable = init_settings_callable
        self.env_settings_callable = env_settings_callable
        self.file_secret_settings_callable = file_secret_settings_callable
        self.loaders = loaders or []
        self.source_priority = source_priority
        self.all_loaded_fields = {}
        self.full_fields = {}

    def load_all(self):
        loaders_dict = {loader.NAME: loader for loader in self.loaders}
        for source in self.source_priority:
            if source is ConfigSource.map:
                continue
            self.all_loaded_fields[source] = {
                field.name: field for field in loaders_dict[source].load_fields(settings=self.settings_obj)
            }

        # Load the map config last.
        if ConfigSource.map in self.source_priority:
            self.all_loaded_fields[ConfigSource.map] = {
                field.name: field for field in loaders_dict[ConfigSource.map].load_fields(settings=self.settings_obj)
            }

        # As needed in `customise_sources`, Create a tuple of callbacks that return dict of fields for every source.
        # The first callable has the highest priority and so on.
        source_fields_callables = (lambda s: self.all_loaded_fields[source] for source in self.source_priority)

        return source_fields_callables
