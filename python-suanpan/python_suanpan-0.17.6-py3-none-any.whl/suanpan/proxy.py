# coding=utf-8
from __future__ import absolute_import, print_function

import copy
import functools

from suanpan import error
from suanpan.imports import imports
from suanpan.objects import HasName


class Proxy(HasName):
    TYPE_KEY = "type"
    DEFAULT_TYPE = None
    MAPPING = {}

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._backend = None
        self._args = args
        self._kwargs = kwargs
        setattr(self, self.TYPE_KEY, kwargs.get(self.TYPE_KEY, self.DEFAULT_TYPE))

    def __call__(self, *args, **kwargs):
        return self.backend(*args, **kwargs)  # pylint: disable=not-callable

    def __getattr__(self, key):
        return getattr(self.__getattribute__("backend"), key)

    def __copy__(self):
        _args = copy.copy(self._args)
        _kwargs = copy.copy(self._kwargs)
        _kwargs[self.TYPE_KEY] = getattr(self, self.TYPE_KEY)
        return self.__class__(*_args, **_kwargs)

    def __deepcopy__(self, meno=None):
        _args = copy.deepcopy(self._args, meno)
        _kwargs = copy.deepcopy(self._kwargs, meno)
        _kwargs[self.TYPE_KEY] = getattr(self, self.TYPE_KEY)
        return self.__class__(*_args, **_kwargs)

    @property
    def backend(self):
        if self._backend is None:
            if getattr(self, self.TYPE_KEY, None) is None:
                raise error.ProxyError(f"{self.name} backend isn't set.")
            self.setBackend(*self._args, **self._kwargs)
        if isinstance(self._backend, functools.partial):
            self._backend = self._backend()
        return self._backend

    def setBackend(self, *args, **kwargs):
        backendType = kwargs.get(self.TYPE_KEY, getattr(self, self.TYPE_KEY, None))
        if not backendType:
            raise error.ProxyError(
                f"{self.name} backend type is required - {self.TYPE_KEY}: {backendType}"
            )
        BackendClass = self.importBackend(backendType)
        _args = [*self._args, *args]
        _kwargs = {**self._kwargs, **kwargs}
        self._backend = self._setBackend(BackendClass, *_args, **_kwargs)
        setattr(self, self.TYPE_KEY, backendType)
        return self

    def importBackend(self, backendType):
        BackendClass = self.MAPPING.get(backendType)
        if not BackendClass:
            raise error.ProxyError(
                f"{self.name} don't supported backend type {backendType}"
            )
        if isinstance(BackendClass, str):
            BackendClass = imports(BackendClass)

        return BackendClass

    def setDefaultBackend(self, *args, **kwargs):
        kwargs.update({self.TYPE_KEY: self.DEFAULT_TYPE})
        return self.setBackend(*args, **kwargs)

    def _setBackend(self, BackendClass, *args, **kwargs):
        if self.TYPE_KEY in kwargs:
            kwargs.pop(self.TYPE_KEY)
        return functools.partial(BackendClass, *args, **kwargs)
