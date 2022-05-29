from .namespace import Namespace
from .python_object_namespace import PythonObjectNamespace


class NoopNamespace(Namespace):
    def __init__(self):
        super(NoopNamespace, self).__init__(self.METHODS)
        self.span = None

    def call_method(self, name, args):
        return PythonObjectNamespace(None)

    def read_key(self, key):
        return PythonObjectNamespace(None)

    def read_attribute(self, name):
        return PythonObjectNamespace(None)

    METHODS = ()
