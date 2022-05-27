import configparser
from typing import NamedTuple, Any

from robertcommonbasic.basic.os.file import check_file_exist, get_file_folder
from robertcommonbasic.basic.os.path import create_dir_if_not_exist
from robertcommonbasic.basic.validation import input as input_checker

class INIConfig(NamedTuple):
    PATH: str
    PARAMS: dict

class INIAccessor:

    def __init__(self, config: INIConfig):
        self.file_path: str = config.PATH
        self.default_params: dict = config.PARAMS
        self.config_params: dict = {}
        self.config_sections: dict = {}
        self.load()

    def load(self):
        self.ini_file()

        self.read_file()

    def ini_file(self):
        folder = get_file_folder(self.file_path)
        if len(folder) > 0:
            create_dir_if_not_exist(folder)

        config = configparser.ConfigParser()
        config.read(self.file_path)

        for section_key in self.default_params.keys():
            for param_key in self.default_params.get(section_key).keys():
                if config.has_section(section_key) is False:
                    config.add_section(section_key)
                if config.has_option(section_key, param_key.lower()) is False:
                    config.set(section_key, param_key.lower(), input_checker.ensure_str(param_key, self.default_params.get(section_key)))

        config.write(open(self.file_path, 'w'))

    def read_file(self):
        config = configparser.ConfigParser()
        config.read(self.file_path)

        for section in config.sections():
            for option in config.options(section):
                self.config_sections[option] = section
                self.config_params[option] = config.get(section, option)

    def get(self, param_key: str, param_value_type: Any=str):
        param_key = param_key.lower()
        if param_value_type is int:
            return input_checker.ensure_not_none_int(param_key, self.config_params)
        elif param_value_type is bool:
            return input_checker.ensure_not_none_bool(param_key, self.config_params)
        elif param_value_type is float:
            return input_checker.ensure_not_none_float(param_key, self.config_params)
        elif param_value_type is str:
            return input_checker.ensure_not_none_str(param_key, self.config_params)
        elif param_value_type is list:
            return input_checker.ensure_not_none_list(param_key, self.config_params)
        else:
            return input_checker.ensure_not_none(param_key, self.config_params)

    def set(self, param_key: str, param_value: Any, section_key: str=None):
        param_key = param_key.lower()
        self.config_params[param_key] = param_value

        config = configparser.ConfigParser()
        config.read(self.file_path)

        if section_key is not None:
            if config.has_section(section_key) is False:
                config.add_section(section_key)
            config.set(section_key, param_key, param_value)
            config.write(open(self.file_path, 'w'))
        else:
            if param_key in self.config_sections.keys():
                config.set(self.config_sections.get(param_key), param_key, param_value)
                config.write(open(self.file_path, 'w'))