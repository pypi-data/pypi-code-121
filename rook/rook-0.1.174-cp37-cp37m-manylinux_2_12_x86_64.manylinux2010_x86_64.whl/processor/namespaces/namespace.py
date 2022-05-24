from rook.exceptions import RookWriteAttributeNotSupported, RookAttributeNotFound, RookMethodNotFound


class Namespace(object):
    def __init__(self, methods=None):
        self._methods = {}

        if methods:
            for method in methods:
                self._methods[method.__name__] = method

    def call_method(self, name, args):
        try:
            method = self._methods[name]
        except KeyError:
            raise RookMethodNotFound(type(self), name)

        return method(self, args)

    def read_attribute(self, name):
        try:
            if hasattr(self, '__dict__') and self.__dict__ and name in self.__dict__:
                return self.__dict__[name]
            if hasattr(self, '__slots__') and self.__slots__ and name in self.__slots__:
                return self.__slots__[name]

            raise RookAttributeNotFound(name)
        except AttributeError:
            raise RookAttributeNotFound(name)

    def write_attribute(self, name, value):
        raise RookWriteAttributeNotSupported(type(self), name)

    def read_key(self, key):
        try:
            return self[key]
        except KeyError:
            raise RookAttributeNotFound(key)
