#!/usr/bin/env python
# coding: utf-8
import numpy as np
import inspect
import random
import string
import types
from collections import Iterable


np.set_printoptions(threshold=np.inf)


def prepare_algorithm_parameters(alg_ps, value=None):
    value = value if value is not None else {}
    options = {}
    if alg_ps is not None:
        for k, v in enumerate(alg_ps):
            key = v['key'] if 'key' in v else None
            option = v['option'] if 'option' in v else None
            val = v['val'] if 'val' in v else None
            if key is not None:
                value[key] = val
                options[key] = option
                if option is not None and type(option) == dict and 'type' in option:
                    value[key] = to_type(val, option['type'])
    return value, options


def prepare_model_parameters(model_ps, value=None, option=None):
    value = value if value is not None else {}
    if model_ps is not None:
        assert (type(model_ps) is dict)
        for k, v in model_ps.items():
            value[k] = v
            if option is not None and type(option) == dict and option.get(k) is not None and type(option[k]) == dict and 'type' in option[k]:
                value[k] = to_type(v, option[k]['type'])
    return value


def to_type(val, t: str):
    t = t.lower()
    if t == 'string' or t == 'str':
        return str(val)
    if t == 'enum':
        return str(val)
    if t == 'integer' or t == 'int':
        return int(val)
    if t == 'double' or t == 'float':
        return float(val)
    if t == 'boolean' or t == 'bool':
        if isinstance(val, bool):
            return val
        return val == 1 or val == '1' or val == 'True' or val == 'true'
    if t == 'array(int)' or t == 'array(integer)':
        return list(map(int, val.split(",")))
    if t == 'array(string)'  or t == 'array(str)':
        return val.split(",")
    if t == 'array(array(int))' or t == 'array(array(integer))':
        return [list(map(int,filter(lambda n:n!="",val.split(","))))]
    return val


def default_dump(obj):
    """Convert numpy classes to JSON serializable objects."""
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def generate_random_str(length=16):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def import_code(code, mod=None, name=None):
    if mod is None:
        # create blank module
        name = name if name is not None else generate_random_str()
        mod = types.ModuleType(name)
    exec(code, mod.__dict__)
    return mod


def get_first_element(mod):
    for element_name in dir(mod):
        element = getattr(mod, element_name)
        if inspect.isclass(element):
            return element()
        elif inspect.isfunction(element):
            return element


def is_empty_function(f):
    """Returns true if f is an empty function."""

    def empty_func():
        pass

    def empty_func_with_docstring():
        """Empty function with docstring."""
        pass

    def empty_lambda(): return None
    def empty_lambda_with_docstring(): return None
    empty_lambda_with_docstring.__doc__ = """Empty function with docstring."""

    def constants(f):
        """Return a tuple containing all the constants of a function without:
            * docstring
        """
        return tuple(
            x
            for x in f.__code__.co_consts
            if x != f.__doc__
        )

    return (
        f.__code__.co_code == empty_func.__code__.co_code and
        constants(f) == constants(empty_func)
    ) or (
        f.__code__.co_code == empty_func_with_docstring.__code__.co_code and
        constants(f) == constants(empty_func_with_docstring)
    ) or (
        f.__code__.co_code == empty_lambda.__code__.co_code and
        constants(f) == constants(empty_lambda)
    ) or (
        f.__code__.co_code == empty_lambda_with_docstring.__code__.co_code and
        constants(f) == constants(empty_lambda_with_docstring)
    )
