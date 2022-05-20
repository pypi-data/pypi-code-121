"""
Copyright 2021 Daniel Afriyie

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import threading

from ru.utils import abstractmethod, get_data
from ru.exceptions.exceptions import ConfigKeyError, ConfigFileNotFoundError


class BaseConfig:
    """"
    Base config class for all config classes
    """

    def __init__(self, config_path):
        self.CONFIG_PATH = config_path
        self._config = self.load()
        self._mutex = threading.RLock()

    @property
    def config(self):
        with self._mutex:
            return self._config

    @abstractmethod
    def save(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_config(self, *args, **kwargs):
        pass

    @staticmethod
    def _cast(item, cast):
        if cast is bool:
            return eval(item.strip().capitalize())
        return cast(item.strip())

    def get(self, item, default=None, cast=None):
        with self._mutex:
            try:
                val = self._config[item]
                if cast:
                    return self._cast(val, cast)
                return val
            except KeyError:
                return default

    def get_as_tupple(self, item, cast=None):
        with self._mutex:
            items = self._config[item].split(',')
            if cast is None:
                return tuple(items)
            return tuple(self._cast(val, cast) for val in items)

    def load(self):
        try:
            return self.load_config()
        except FileNotFoundError:
            raise ConfigFileNotFoundError(f"{self.__class__.__name__}: Config file '{self.CONFIG_PATH}' not found!")

    def __getitem__(self, item):
        with self._mutex:
            try:
                if isinstance(item, list):
                    items = [self._config[key] for key in item]
                    return items
                else:
                    return self._config[item]
            except KeyError:
                raise ConfigKeyError(f"{item}")

    def __setitem__(self, key, value):
        with self._mutex:
            self._config[key] = value

    def __repr__(self):
        return str(self._config)


class JsonConfig(BaseConfig):

    def __init__(self, config_path='config.json'):
        super().__init__(config_path)

    def load_config(self):
        with open(self.CONFIG_PATH, encoding='utf-8') as f:
            config = json.load(f)
        return config

    def save(self, filename='config.json', encoding='utf-8'):
        with open(filename, 'w') as f:
            json.dump(self._config, f, indent=4)


class TextConfig(BaseConfig):

    def __init__(self, config_path='config.txt'):
        super().__init__(config_path)

    def load_config(self):
        config = {}
        data = get_data(self.CONFIG_PATH, split=True, split_char='\n')
        for d in data:
            try:
                key, val = d.split('=')
                config[key.strip()] = val
            except ValueError:
                pass
        return config

    def save(self, filename='config.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            len_config = len(self._config) - 1
            for idx, key in enumerate(self._config):
                f.write(f"{key}={self._config[key]}")
                if idx < len_config:
                    f.write('\n')
