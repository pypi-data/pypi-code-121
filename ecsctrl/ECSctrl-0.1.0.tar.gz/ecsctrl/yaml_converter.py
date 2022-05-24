from typing import Dict, List
import yaml

from .loader import SpecFileLoader
from functools import partial

TASK_DEFINITION = "taskDefinition"
SERVICE = "service"


def expand_key_value_list(key_field: str, value_field: str, obj: dict):
    if isinstance(obj, dict):
        return [{key_field: k, value_field: v} for k, v in obj.items()]

    elif isinstance(obj, list):
        result = []
        for i in obj:
            if isinstance(i, str) and "=" in i:
                k, v = i.split("=", maxsplit=2)
                result.append({key_field: k, value_field: v})

            elif isinstance(i, dict):
                result.append(i)

            else:
                raise ValueError()
        return result

    else:
        raise ValueError()


TRANSFORMATIONS = {
    TASK_DEFINITION: {
        "containerDefinitions.*.environment": partial(
            expand_key_value_list, "name", "value"
        ),
        "containerDefinitions.*.secrets": partial(
            expand_key_value_list, "name", "valueFrom"
        ),
        "proxyConfiguration.properties": partial(
            expand_key_value_list, "name", "value"
        ),
        "tags": partial(expand_key_value_list, "key", "value"),
        "cpu": str,
        "memory": str,
    },
    SERVICE: {
        "tags": partial(expand_key_value_list, "key", "value"),
    },
}


def _apply_function_to_path(obj: dict, path: str, function: callable):
    exploded_path = path.split(".")
    next_level = exploded_path[0]

    if len(exploded_path) > 1:
        next_path = ".".join(exploded_path[1:])
        if next_level == "*" and isinstance(obj, list):
            for next_obj in obj:
                _apply_function_to_path(next_obj, next_path, function)
        elif isinstance(obj, dict) and next_level in obj:
            _apply_function_to_path(obj[next_level], next_path, function)

    if len(exploded_path) == 1 and next_level in obj:
        obj[next_level] = function(obj[next_level])


def yaml_data_to_dict(obj: dict):
    for path, function in TRANSFORMATIONS[TASK_DEFINITION].items():
        _apply_function_to_path(obj, path, function)
    return obj


def yaml_to_dict(yaml_contents: str):
    return yaml_data_to_dict(yaml.load(yaml_contents, Loader=yaml.Loader))


def yaml_file_to_dict(
    file_path: str,
    vars: Dict[str, str],
):
    loader = SpecFileLoader(file_path, vars)
    raw_yaml = loader.load()
    return yaml_to_dict(raw_yaml)
