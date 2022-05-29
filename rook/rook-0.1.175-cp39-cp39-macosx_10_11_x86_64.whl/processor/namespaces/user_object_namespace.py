from .dumped_object_namespace import DumpedObjectNamespace


class UserObjectNamespace(DumpedObjectNamespace):

    def __init__(self, type, attributes):
        super(UserObjectNamespace, self).__init__(type, u'UserObject', attributes)
