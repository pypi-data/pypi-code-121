
from collections.abc import MutableMapping

class Row(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        if not key in list(self.keys()) and type(key) == int:
            key = list(self.keys())[key]
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def __repr__(self):
        return self.store.__repr__()

    def show(self):
        for k, v in self.store.items():
            print('   {:20} {}'.format(k,v))

    def keys(self):
        return list(super().keys())
