from .python_object_namespace import PythonObjectNamespace
from .dumped_primitive_namespace import DumpedPrimitiveNamespace


class StringNamespace(DumpedPrimitiveNamespace):

    def __init__(self, obj, original_size, type, common_type, attributes={}):
        super(StringNamespace, self).__init__(obj, type, common_type, attributes, self.METHODS)
        self.original_size = original_size

    def size(self, args):
        return PythonObjectNamespace(len(self.obj))

    def original_size(self, args):
        return PythonObjectNamespace(self.original_size)

    METHODS = (size, original_size)
