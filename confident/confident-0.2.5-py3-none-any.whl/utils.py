import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from pydantic import BaseSettings


def load_file(path: Union[Path, str]) -> Dict[str, Any]:
    """
    Loads fields from a file into a dictionary.

    Args:
        path: Path to the file to load.
    """
    path = Path(path)

    if not path.is_file():
        raise ValueError(f'{path=} is not exists.')

    if path.suffix == '.json':
        with open(path, mode='r') as file:
            return json.load(file)

    if path.suffix == '.yaml':
        with open(path, mode='r') as file:
            return yaml.safe_load(file)

    raise ValueError(f'{path=} is not a supported file.')


def get_class_file_path(cls: object) -> Union[str, Path]:
    """
    Gets the path that the config class is initiated from.
    Tries to find the path of the caller module.
    If there is no module that called this class constructor, returns the current working path.
    Mainly happens when running on terminal.
    """
    try:
        return importlib.import_module(cls.__module__).__file__
    except (AttributeError, ImportError):
        return Path.cwd()


def convert_field_value(settings: BaseSettings, field_name: str, origin_value: Any) -> Any:
    """
    Tries to convert the field value to the right type in the declaration annotation.
    If nothing works, do nothing and let pydantic `BaseSettings` `__init__` call handle the validation.
    Args:
        settings: The BaseSetting object with all config fields to be loaded.
        field_name: The name of the attribute to find its expected type.
        origin_value: The original value retrieved from the config source.

    Returns:
        The converted origin value. Can also be untouched.
    """
    model_field = settings.__fields__.get(field_name)
    # model_field.outer_type_ can be type annotation and not type.
    if (model_field and isinstance(model_field.outer_type_, type)
            and isinstance(origin_value, model_field.outer_type_)):
        return origin_value
    if isinstance(origin_value, str):
        try:
            return json.loads(origin_value)
        except (TypeError, ValueError):
            pass
    return origin_value
