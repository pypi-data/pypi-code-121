#!/usr/bin/env python
# coding: utf-8

from ctypes import Union
import inspect
from inspect import signature
from typing import Tuple
import intelliw.utils.message as message


def is_valid_algorithm(mod) -> Tuple[bool, message.CommonResponse]:
    if not inspect.ismodule(mod):
        return False, message.err_missing_algorithm_mod

    if not (hasattr(mod, 'Algorithm') and inspect.isclass(mod.Algorithm)):
        return False, message.err_missing_algorithm_class

    cls = mod.Algorithm
    if not (hasattr(cls, 'train') and inspect.isfunction(cls.train)):
        return False, message.err_missing_train_method
    else:
        sig = signature(cls.train)
        if len(sig.parameters) < 2 or 'self' not in sig.parameters:
            return False, message.err_missing_train_parameter

    if not (hasattr(cls, 'infer') and inspect.isfunction(cls.infer)):
        return False, message.err_missing_infer_method
    else:
        sig = signature(cls.infer)
        if len(sig.parameters) < 1 or 'self' not in sig.parameters:
            return False, message.err_missing_infer_parameter

    if not (hasattr(cls, '__init__') and inspect.isfunction(cls.__init__)):
        return False, message.err_missing_init_method
    else:
        sig = signature(cls.__init__)
        if len(sig.parameters) != 2 or 'self' not in sig.parameters:
            return False, message.err_missing_init_parameter

    if not (hasattr(cls, 'load') and inspect.isfunction(cls.load)):
        return False, message.err_missing_load_method
    else:
        sig = signature(cls.load)
        if len(sig.parameters) != 2 or 'self' not in sig.parameters:
            return False, message.err_missing_load_parameter

    if not (hasattr(cls, 'save') and inspect.isfunction(cls.save)):
        return False, message.err_missing_save_method
    else:
        sig = signature(cls.save)
        if len(sig.parameters) != 2 or 'self' not in sig.parameters:
            return False, message.err_missing_save_parameter

    return True, None

