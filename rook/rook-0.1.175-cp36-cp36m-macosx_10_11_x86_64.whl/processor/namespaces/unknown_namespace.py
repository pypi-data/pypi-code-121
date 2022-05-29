
from .dumped_object_namespace import DumpedObjectNamespace


class UnknownNamespace(DumpedObjectNamespace):

    def __init__(self, type, attributes={}):
        super(UnknownNamespace, self).__init__(type, "UnknownObject", attributes)
