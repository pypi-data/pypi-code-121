import datetime

from .dumped_object_namespace import DumpedObjectNamespace


# TODO - remove this class
class DumpedPrimitiveNamespace(DumpedObjectNamespace):

    def __init__(self, obj, type, common_type, attributes={}, methods=()):
        super(DumpedPrimitiveNamespace, self).__init__(type, common_type, attributes, methods)
        self.obj = obj

    def _get_value_for_json(self):
        if isinstance(self.obj, complex):
            return {u'real': self.obj.real, u'imag': self.obj.imag}
        elif isinstance(self.obj, datetime.datetime):
            return str(self.obj)
        else:
            return self.obj
