#-----------------------------
# -- fundb --
# lib module
#-----------------------------

import uuid
import datetime
from typing import Any
from ctypes import Union
from functools import reduce

def get_timestamp() -> datetime.datetime:
    """
    Generates the current UTC timestamp

    Returns:
      int
    """
    return datetime.datetime.now()


def gen_id() -> str:
    """
    Generates a unique ID

    Returns:
      string
    """
    return str(uuid.uuid4()).replace("-", "")


def dict_merge(*dicts) -> dict:
    """         
    Deeply merge an arbitrary number of dicts                                                                    
    Args:
        *dicts
    Return:
        dict

    Example
        dict_merge(dict1, dict2, dict3, dictN)
    """
    updated = {}
    # grab all keys
    keys = set()
    for d in dicts:
        keys = keys.union(set(d))

    for key in keys:
        values = [d[key] for d in dicts if key in d]
        maps = [value for value in values if isinstance(value, dict)]
        if maps:
            updated[key] = dict_merge(*maps)
        else:
            updated[key] = values[-1]
    return updated


def _get_nested_default(d, path):
    return reduce(lambda d, k: d.setdefault(k, {}), path, d)


def _set_nested(d, path, value):
    _get_nested_default(d, path[:-1])[path[-1]] = value


def flatten_dict(ddict: dict, prefix='') -> dict:
    """
    To flatten a dict. Nested node will be separated by dot or separator

    Args:
      ddict:
      prefix:
    Returns:
      dict
    """
    return {prefix + "." + k if prefix else k: v
            for kk, vv in ddict.items()
            for k, v in flatten_dict(vv, kk).items()
            } if isinstance(ddict, dict) else {prefix: ddict}


def unflatten_dict(flatten_dict: dict) -> dict:
    """
    To un-flatten a flatten dict

    Args:
      flatten_dict: A flatten dict
    Returns:
      an unflatten dictionnary
    """
    output = {}
    for k, v in flatten_dict.items():
        path = k.split(".")
        _set_nested(output, path, v)
    return output



def dict_set(obj:dict, path:str, value:Any):
    """
    *Mutate #obj

    Update a dict via dotnotation

    Args:
        obj:dict - This object will be mutated
        path:str - the dot notation path to update
        value:Any - value to update with

    Returns:
        None
    """
    here = obj
    keys = path.split(".")
    for key in keys[:-1]:
        here = here.setdefault(key, {})
    here[keys[-1]] = value


def dict_get(obj:dict, path:str, default:Any=None) -> dict:
    """
    Get a value from a dict via dot notation

    Args:
        obj: Dict
        path: String - dot notation path
            object-path: key.value.path
            object-with-array-index: key.0.path.value
    Returns:
        mixed
    """
    def _getattr(obj, path):
        try:
            if isinstance(obj, list) and path.isdigit():
                return obj[int(path)]
            return obj.get(path, default)
        except:
            return default
    return reduce(_getattr, [obj] + path.split('.'))

def dict_pop(obj:dict, path:str) -> Any:
    """
    * Mutates #obj

    To pop a property from a dict dotnotation

    Args:
        obj:dict - This object will be mutated
        path:str - the dot notation path to update
        value:Any - value to update with

    Returns:
        Any - The value that was removed
    """

    here = obj 
    keys = path.split(".")

    for key in keys[:-1]:
        here = here.setdefault(key, {})
    if isinstance(here, dict):
        return here.pop(keys[-1])
    else:
        val = here[keys[-1]]
        del here[keys[-1]]
        return val

