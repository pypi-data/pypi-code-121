__version__ = '22.2.1.1'

import re
class Flow360Version:
    def __init__(self, version):
        self.full = version
        ret = re.findall('^([a-zA-Z0-9\-]+)-([0-9\.]+)$', version)
        if len(ret) != 1:
            print('matched version = '+str(ret))
            raise RuntimeError('solver version is not valid: {}'.format(version))
        self.head = ret[0][0]
        self.tail = [int(i) for i in ret[0][1].strip().split('.')]

    def __lt__(self, other):
        return self.tail < other.tail

    def __le__(self, other):
        return self.tail <= other.tail

    def __gt__(self, other):
        return self.tail > other.tail

    def __ge__(self, other):
        return self.tail >= other.tail

    def __eq__(self, other):
        return self.tail == other.tail and self.head == other.head

    def __ne__(self, other):
        return self.tail != other.tail or self.head != other.head

