# coding=utf-8
from __future__ import absolute_import, print_function

import os

environ = os.environ


def String(value):
    return str(value)


def Int(value):
    return int(value)


def Float(value):
    return float(value)


def Bool(value):
    return value in ("true", "True")


def lazyget(
    key, default=None, required=False, type=String
):  # pylint: disable=used-before-assignment
    return property(
        lambda self: get(key, default=default, required=required, type=type)
    )


def get(key, default=None, required=False, type=String):
    if key not in environ:
        if required:
            raise Exception(f"No such env: {key}")
        return default
    value = environ[key]
    try:
        return type(value)
    except Exception as e:
        raise Exception(f"EnvTypeErr: ({key}) {value} except {getTypeName(type)}") from e


def getTypeName(type):
    name = getattr(type, "name", None) or getattr(type, "__name__", None)
    if not name:
        raise Exception(f"Unknown env type: {type}")
    return name


def update(*args, **kwargs):
    return environ.update(*args, **kwargs)
