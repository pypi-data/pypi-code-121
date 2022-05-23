# coding=utf-8
from __future__ import absolute_import, print_function

import collections

from suanpan.log import logger


class Module(object):
    def __init__(self, enabled=True):
        super().__init__()
        self._enabled = enabled
        self.handlers = collections.defaultdict(list)
        self.streamHandlers = collections.defaultdict(list)
        self.constants = {}
        self.functions = {}
        self.bootstraps = {}

    def enable(self):
        self._enabled = True
        return self

    def disable(self):
        self._enabled = False
        return self

    @property
    def enabled(self):
        return self._enabled

    def on(self, event):
        def _dec(func):
            self.handlers[event].append(func)
            return func

        return _dec

    def stream(self, event):
        def _dec(func):
            self.streamHandlers[event].append(func)
            return func

        return _dec

    def fn(self, fn):
        self.functions[fn.__name__] = fn
        return fn

    def const(self, key, value):
        self.constants[key] = value
        return value

    def __getattr__(self, key):
        if key in self.constants:
            return self.constants[key]
        if key in self.functions:
            return self.functions[key]
        return self.__getattribute__(key)

    def _bootstrap(self):
        for _, bootstrap in self.bootstraps.items():
            bootstrap()

    def _onBootstrap(self, fn):
        self.bootstraps[fn.__name__] = fn
        return fn

    def bootstrap(self, fn=None):
        if fn:
            return self._onBootstrap(fn)
        return self._bootstrap()


class Modules(object):
    def __init__(self):
        super().__init__()
        self.modules = {}

    def __getattr__(self, key):
        if key in self.modules:
            return self.modules[key]
        return self.__getattribute__(key)

    def register(self, name, module, enable=True):
        module = module.enable() if enable else module.disable()
        self.modules[name] = module
        return module

    @property
    def handlers(self):
        _handlers = collections.defaultdict(list)
        for module in self.modules.values():
            if module.enabled:
                for event, fns in module.handlers.items():
                    _handlers[event].extend(fns)
        return _handlers

    @property
    def streamHandlers(self):
        _handlers = collections.defaultdict(list)
        for module in self.modules.values():
            if module.enabled:
                for event, fns in module.streamHandlers.items():
                    _handlers[event].extend(fns)
        return _handlers

    def enable(self, name):
        return self.modules[name].enable()

    def disable(self, name):
        return self.modules[name].disable()

    def info(self):
        for name, module in self.modules.items():
            enabledStr = "Enabled" if module.enabled else "Disabled"
            logger.debug(f"App Module {name}: {enabledStr}")

    def bootstrap(self):
        for _, module in self.modules.items():
            if module.enabled:
                module.bootstrap()
