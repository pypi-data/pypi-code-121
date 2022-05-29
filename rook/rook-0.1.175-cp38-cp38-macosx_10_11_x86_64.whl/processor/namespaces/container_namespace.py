from .namespace import Namespace

from .python_object_namespace import PythonObjectNamespace

from rook.exceptions import RookAttributeNotFound


class ContainerNamespace(dict, Namespace):
    def __init__(self, dictionary=None):
        Namespace.__init__(self, self.METHODS)
        dict.__init__(self, dictionary or {})

    def read_attribute(self, name):
        try:
            return self[name]
        except KeyError:
            raise RookAttributeNotFound(name)

    def write_attribute(self, name, value):
        self[name] = value

    def size(self, args):
        return PythonObjectNamespace(len(self))

    def __getattr__(self, item):
        if item == u'dictionary':
            return self
        elif item in self:
            return self[item]
        else:
            return dict.__getattribute__(self, item)

    METHODS = (size,)
