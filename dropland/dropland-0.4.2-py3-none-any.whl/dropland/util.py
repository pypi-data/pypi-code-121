import os
import re
from typing import Any, Dict, List, Callable, Iterable


def snake2kebab(string: str) -> str:
    return re.sub('_', '-', string)


def kebab2snake(string: str) -> str:
    return re.sub('-', '_', string)


def snake2camel(string: str, upper: bool = False) -> str:
    result = []

    for i, word in enumerate(string.split('_')):
        if upper or i > 0:
            word = word.capitalize()
        result.append(word)

    return ''.join(result)


def default_value(type_: type):
    def getter(value: Any, default: Any):
        return type_(value) if value is not None else default
    return getter


def expandvars_dict(settings_dict):
    """Expands all environment variables in a settings dictionary."""
    return dict((key, os.path.expandvars(value)) for key, value in settings_dict.items())


def prepare_enum_keys(enum_class):
    return [snake2kebab(str(e.value).lower()) for e in enum_class]


def dict_values_to_str(data: dict):
    for k, v in data.items():
        if isinstance(v, str):
            pass
        elif isinstance(v, dict):
            v = dict_values_to_str(v)
        else:
            v = str(v)

        data[str(k)] = v

    return data


def build_dict_from_dotted_keys(
        iterable: Iterable, key_getter: Callable[[Any], Any],
        value_getter: Callable[[Any], Any])\
        -> Dict[str, Any]:
    result = {}

    for obj in iterable:
        keys = key_getter(obj).split('.')
        cur_dict = result

        for key in keys[:-1]:
            if key not in cur_dict:
                cur_dict[key] = {}

            if not isinstance(cur_dict[key], dict):
                cur_dict[key] = {'.': cur_dict[key]}
            cur_dict = cur_dict[key]

        cur_dict[keys[-1]] = value_getter(obj)

    return result


def build_dotted_keys_from_dict(dict_: Dict[str, Any], root_key: str = None) -> Dict[str, Any]:
    def traverse(key_stack: List[str], values: Dict[str, Any]) -> Dict[str, Any]:
        res = {}

        for k, v in values.items():
            if isinstance(v, dict):
                res.update(traverse(key_stack + [k], v))
            elif isinstance(v, list):
                for i in v:
                    i = traverse(key_stack + [k], i)
                    if isinstance(i, dict):
                        res |= i
            else:
                res['.'.join(key_stack + [k])] = v

        return res

    return traverse([root_key] if root_key else [], dict_)


def obj_dict_to_str_dict(data: dict, value_getter: Callable[[Any], Any]):
    def traverse(values: Dict[str, Any]) -> Dict[str, Any]:
        res = {}

        for k, v in values.items():
            if isinstance(v, dict):
                res[k] = traverse(v)
            elif v is None:
                pass
            else:
                res[k] = value_getter(v)

        return res

    return traverse(data)
