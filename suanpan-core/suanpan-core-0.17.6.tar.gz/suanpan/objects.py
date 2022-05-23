# coding=utf-8
from __future__ import absolute_import, print_function

from addict import Dict


class HasName(object):
    @property
    def name(self):
        return self.__class__.__name__


class Context(Dict, HasName):
    @classmethod
    def froms(cls, *args, **kwargs):
        context = cls()
        context.update(item for arg in args for item in arg.items())
        context.update(kwargs)
        return context

    def __getitem__(self, name):
        value = super().__getitem__(name)
        if isinstance(value, property):
            value = value.fget(self)
            self.__setitem__(name, value)
        return value

    def json(self, keys=None):
        keys = keys or self.keys()
        return {key: self[key] for key in keys if self._isJsonable(key)}

    def _isValid(self, key):
        try:
            self.__getitem__(key)
            return True
        except Exception:  # pylint: disable=broad-except
            return False

    def _isJsonable(self, key):
        jsonableTypes = (str, int, float, bool, dict, list)
        return self._isValid(key) and isinstance(self[key], jsonableTypes)
