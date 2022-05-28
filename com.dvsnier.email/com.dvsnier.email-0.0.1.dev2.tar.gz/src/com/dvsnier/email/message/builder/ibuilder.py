# -*- coding:utf-8 -*-


class IBuilder(object):
    '''the build class'''

    def __init__(self):
        super(IBuilder, self).__init__()

    def build(self):
        '''
            the build method:

                1. build mime object
                2. the transmit what config object
                3. set subject and MIME type custom datasets
                4. the execute function what is callback
                5. the configure mime object
        '''
        pass
