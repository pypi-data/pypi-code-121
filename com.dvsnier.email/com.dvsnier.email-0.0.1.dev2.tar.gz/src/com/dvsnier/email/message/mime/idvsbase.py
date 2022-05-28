# -*- coding:utf-8 -*-

class IDvsBase(object):
    ''' the dvsnier base class '''

    # type: Union[IAttribute, None] or Optional[IAttribute]
    _attribute = None

    def __init__(self):
        super(IDvsBase, self).__init__()

    def get_attribute(self):
        ''' the get message '''
        return self._attribute

    def set_attribute(self, attribute):
        ''' the set message '''
        self._attribute = attribute
        return self
