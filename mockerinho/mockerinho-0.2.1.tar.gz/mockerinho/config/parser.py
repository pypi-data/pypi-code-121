import functools
import json
import os

import schema
import yaml

from .schema import config_file_schema
from ..errors import IncorrectConfigFileSchemaError, ParsingConfigFileError


def handle_load_error(to_except):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except to_except as err:
                raise ParsingConfigFileError(err)

        return wrapper

    return decorator


class ConfigFileParser:
    @staticmethod
    def parse(path: str) -> dict:
        name, extension = os.path.splitext(path)

        if extension.lower() in ('.yml', '.yaml'):
            parsed = ConfigFileParser.__load_yaml(path)
        elif extension.lower() == '.json':
            parsed = ConfigFileParser.__load_json(path)
        else:
            message = f'Disallowed config extension for "{name}" file: {extension}'
            raise ParsingConfigFileError(message)

        try:
            config = config_file_schema.validate(parsed)
        except schema.SchemaError as err:
            raise IncorrectConfigFileSchemaError(err)

        return config

    @staticmethod
    @handle_load_error(yaml.YAMLError)
    def __load_yaml(path: str) -> dict:
        with open(path) as yaml_file:
            loaded_dict = yaml.safe_load(yaml_file)
            return loaded_dict

    @staticmethod
    @handle_load_error(json.JSONDecodeError)
    def __load_json(path: str) -> dict:
        with open(path) as json_file:
            loaded_dict = json.load(json_file)
            return loaded_dict
