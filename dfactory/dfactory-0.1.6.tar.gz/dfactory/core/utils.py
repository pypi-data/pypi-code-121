# -*- coding: utf-8 -*-

"""
utils
"""

from importlib import import_module


def import_class(class_path: str):
    """
    import a class
    :param class_path: class name with path
    :return: class
    """
    components = class_path.rsplit(".", 1)
    if len(components) == 1 or "" == components[0]:
        return import_module(class_path)
    mod = import_module(components[0])
    mod = getattr(mod, components[1])
    return mod
