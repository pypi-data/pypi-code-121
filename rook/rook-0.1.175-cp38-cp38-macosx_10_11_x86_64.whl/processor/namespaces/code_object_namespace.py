
from .python_object_namespace import PythonObjectNamespace
from .dumped_object_namespace import DumpedObjectNamespace


class CodeObjectNamespace(DumpedObjectNamespace):

    def __init__(self, name, module, filename, lineno, type, attributes={}):
        super(CodeObjectNamespace, self).__init__(type, u'code', attributes, self.METHODS)

        self.name = name
        self.module = module
        self.filename = filename
        self.lineno = lineno

    def name(self, args):
        return PythonObjectNamespace(self.name)

    def module(self, args):
        return PythonObjectNamespace(self.module)

    def filename(self, args):
        return PythonObjectNamespace(self.filename)

    def lineno(self, args):
        return PythonObjectNamespace(self.lineno)

    METHODS = (name, module, filename, lineno)
