from .namespace import Namespace
from .python_object_namespace import PythonObjectNamespace


class DumpedObjectNamespace(Namespace):

    def __init__(self, type, common_type, attributes, methods=()):
        super(DumpedObjectNamespace, self).__init__(methods + (DumpedObjectNamespace.type, ))
        self.type = type
        self.common_type = common_type
        self.attributes = attributes

    def read_attribute(self, name):
        return self.attributes[name]

    def no_attriubtes(self):
        return 0 == len(self.attributes)

    def read_key(self, key):
        raise NotImplementedError()

    def type(self, args=None):
        return PythonObjectNamespace(self.type)

    def serialize_type(self):
        return type
