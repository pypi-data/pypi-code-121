import time, os
from collections import deque
from random import choices
from .mathtool import base10_to_base36 as Base36Encode


class ContIndex(): ...

class pk_factory():

    def __init__(self):
        pid = Base36Encode(os.getpid())
        random = ''.join(choices('0123456789abcdefghijklmnopqrstuvwxyz', k=10))
        self.mark = f"{pid}-{random}"
        self.ContIds = []
        self.ContPool = deque()
    
    def pk1(self):
        t = Base36Encode( int(time.time() * 1000) )
        try:
            cont = self.ContPool.popleft()
        except:
            cont = [0, 0]
            contid = ContIndex()
            self.ContIds.append(contid)
            cont[0] = Base36Encode(self.ContIds.index(contid))
        cont[1] += 1
        pk = f"{t}-{self.mark}-{cont[0]}-{Base36Encode(cont[1])}"
        self.ContPool.append(cont)
        return pk


x = pk_factory()
pk1 = x.pk1
