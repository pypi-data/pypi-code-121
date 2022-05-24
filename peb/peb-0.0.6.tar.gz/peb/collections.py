import collections
from collections.abc import Iterable, Mapping


def wrap_list(some):
    if isiter(some, allow_dict=False):
        return some
    return [some]


def isiter(arg, allow_dict=True, allow_str=False):
    if not isinstance(arg, Iterable):
        return False
    elif type(arg) is str and not allow_str:
        return False
    elif type(arg) is dict and not allow_dict:
        return False
    else:
        return True


def chunk_iter(iterable, size):
    arr = []
    for some in iterable:
        arr.append(some)
        if len(arr) >= size:
            yield arr
            arr = []
    if len(arr) > 0:
        yield arr


class MutableMapping(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
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


def deep_update(source, d):
    for k, v in d.items():
        if isinstance(v, Mapping):
            source[k] = deep_update(source.get(k, {}), v)
        else:
            source[k] = v
    return source
