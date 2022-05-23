import os
from os.path import exists
from configparser import ConfigParser
from properties_loader.inmutables import _EnvVars
from properties_loader.inmutables import _DfValues
from properties_loader.interfaces import LoadConfig, Properties
from properties_loader.inmutables import _PriorityProperties
from properties_loader.exceptions import PropertiesNotFoundError


class LoadConfigImpl(LoadConfig):

    _priority: int = 0
    _root_path: str
    _path_file: str

    def __init__(self, root_path: str = None, path_file: str = None):
        self._root_path = root_path
        self._path_file = path_file
        self.__load_parameters()
        if self._priority == 0:
            self.__load_env_vars()
        if self._priority == 0:
            self.__load_default()
        if self._priority == 0:
            raise PropertiesNotFoundError(path_file)

    def __load_parameters(self):
        root_path = self._root_path
        path_file = self._path_file
        if root_path and path_file and self.__check_properties():
            self._priority = int(_PriorityProperties.PARAMS)

    def __load_env_vars(self):
        self._root_path = os.getenv(_EnvVars.ROOT_PATH)
        self._path_file = os.getenv(_EnvVars.CONFIG_FILE)
        root_path = self._root_path
        path_file = self._path_file
        if root_path and path_file and self.__check_properties():
            self._priority = int(_PriorityProperties.ENVS_VARS)

    def __load_default(self):
        self._root_path = _DfValues.DF_ROOT_PATH
        self._path_file = _DfValues.DF_PATH_FILE
        if self.__check_properties():
            self._priority = int(_PriorityProperties.ENVS_VARS)
        else:
            path_file: str = f"{self._root_path}/{self._path_file}"
            raise PropertiesNotFoundError(path_file)

    def __check_properties(self):
        return exists(f'{self._root_path}/{self._path_file}')

    @property
    def path_properties(self) -> str:
        return f'{self._root_path}/{self._path_file}'


class PropertiesImpl(LoadConfigImpl, Properties):

    _root_path: str
    _path_file: str

    def __init__(self, root_path: str = None, path_file: str = None):
        super(PropertiesImpl, self).__init__(root_path=root_path, path_file=path_file)

    def __load_configparser(self):
        config_parser = ConfigParser()
        path_file: str = f"{self._root_path}/{self._path_file}"
        try:
            config_parser.read(path_file)
        except Exception:
            from properties_loader.exceptions import PropertiesNotFoundError
            raise PropertiesNotFoundError(path_file)
        else:
            return config_parser

    @property
    def __dict__(self) -> dict:
        properties_to_json: dict = {}
        config_parser: ConfigParser = self.__load_configparser()
        for section in config_parser.sections():
            keys_values_json = {}
            for key in config_parser.options(section):
                keys_values_json[key] = config_parser[section][key]
            properties_to_json[section] = keys_values_json
        return properties_to_json




class PropertiesClassLoader(PropertiesImpl):
    __groups: list

    def __init__(self, root_path: str = None, path_file: str = None, groups: list = None):
        super(PropertiesClassLoader, self).__init__(root_path=root_path, path_file=path_file)
        self.__load_parameters(groups)
        self.__efective_properties = self.__load_efective_properties()
        self.__load_properties()

    def __load_parameters(self, groups: list):
        self.__groups = self.__load_groups(groups)

    def __load_properties(self):
        for group in self.__efective_properties.keys():
            setattr(self, f'_{group}', self.__efective_properties.get(group))

    def __load_efective_properties(self):
        if self.__groups is None:
            return self.__dict__

        json_data: dict = {}
        for group in self.__dict__.keys():
            if group in self.__groups:
                json_data[group] = self.__dict__.get(group)
        return json_data

    def __load_groups(self, groups):
        if groups:
            return groups
        return []

    @property
    def efective_properties(self):
        return self.__efective_properties
