# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import error, objects
from suanpan.stream import handlers


class HasHandlers(objects.HasName):
    def __init__(self):
        super().__init__()
        self.handlers = {}

    def addHandler(self, key, handler):
        if not isinstance(handler, handlers.Handler):
            raise error.StreamInvalidHandlerError(f"{self.name}.{key}")
        if self.hasHandler(key):
            raise error.StreamHandlerExistsError(f"{self.name}.{key}")
        self.setHandler(key, handler)
        return self

    def hasHandler(self, key):
        return key in self.handlers

    def getHandler(self, key):
        handler = self.handlers.get(key)
        if not handler:
            raise error.StreamUnknownHandlerError(f"{self.name}.{key}")
        return handler

    def setHandler(self, key, handler):
        self.handlers[key] = handler
        return self

    def removeHandler(self, key):
        handler = self.handlers.pop(key, None)
        if not handler:
            raise error.StreamUnknownHandlerError(f"{self.name}.{key}")
        return handler
