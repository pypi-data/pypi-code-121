from typing import Union, Dict
from json import dumps, loads
from base64 import b64encode, b64decode

from .tl_object import TLObject
from telectron import raw


def default(obj: TLObject) -> Union[Dict[str, str]]:
    if isinstance(obj, bytes):
        return {'b': b64encode(obj).decode()}

    return {
        "_": obj.QUALNAME,
        **{
            attr: getattr(obj, attr)
            for attr in obj.__slots__
            if getattr(obj, attr) is not None
        }
    }


def loads_tlobject(json):
    return parse_dict(loads(json))


def dumps_tlobject(tlobject, ensure_ascii=False):
    return dumps(tlobject, default=default, ensure_ascii=ensure_ascii)


def parse_dict(obj):
    if type(obj) == dict:
        if obj.get('_', False):
            class_name = raw
            kwargs = {}
            qualname = obj.pop('_')
            for step in qualname.split('.'):
                class_name = getattr(class_name, step)
            for key, value in obj.items():
                kwargs[key] = parse_dict(value)
            return class_name(**kwargs)
        elif obj.get('b', False):
            return b64decode(obj['b'])
        else:
            kwargs = {}
            for key, value in obj.items():
                kwargs[key] = parse_dict(value)
            return kwargs
    elif type(obj) == list:
        return [parse_dict(value) for value in obj]
    elif type(obj) == str:
        return obj
    else:
        return obj
