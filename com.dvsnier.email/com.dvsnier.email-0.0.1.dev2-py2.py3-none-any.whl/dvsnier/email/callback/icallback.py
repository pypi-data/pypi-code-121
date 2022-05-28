# -*- coding:utf-8 -*-


class ICallback(object):
    ''' the callback interface class '''

    def __init__(self):
        super(ICallback, self).__init__()

    def callback(self):
        ''' the callback method '''
        pass
