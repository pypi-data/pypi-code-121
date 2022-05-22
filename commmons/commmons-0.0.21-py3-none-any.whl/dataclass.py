from dataclasses import is_dataclass, fields
from typing import get_origin, get_args

__all__ = [
    "as_dataclass",
    "as_dataclass_list"
]


def as_dataclass(dct: dict, cls: type):
    kwargs = {}
    for fld in fields(cls):
        if fld.name in dct:
            origin = get_origin(fld.type)
            if origin:
                cls_arg = get_args(fld.type)[-1]
                is_dc = is_dataclass(cls_arg)
                if origin == list and is_dc:
                    kwargs[fld.name] = [as_dataclass(element, cls_arg) for element in dct[fld.name]]
                elif origin == dict and is_dc:
                    kwargs[fld.name] = {k: as_dataclass(v, cls_arg) for k, v in dct[fld.name].items()}
            elif is_dataclass(fld.type):
                kwargs[fld.name] = as_dataclass(dct[fld.name], fld.type)
            if not fld.name in kwargs:
                kwargs[fld.name] = dct[fld.name]
    return cls(**kwargs)


def as_dataclass_list(lst: list, cls: type):
    return [as_dataclass(element, cls) for element in lst]
