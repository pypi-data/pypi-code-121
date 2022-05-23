import numpy as np

from typing import Union

numeric = Union[int, float]

MAX_CACHE_SIZE_BYTES = 4e9


class Cache:
    """
    A basic cache to store results of large computations. Rather than using count, this uses a configurable memory size
    """

    def __init__(self, max_cache_size_bytes: numeric = MAX_CACHE_SIZE_BYTES):
        self.max_cache_size_bytes = max_cache_size_bytes
        self.size = 0

        self.cache_dict = dict()
        self.use_size = dict()

    def __len__(self):
        return self.cache_dict.__len__()

    def clear(self):
        for k in self.cache_dict.keys():
            x = self.pop(k)
            del x

    def __setitem__(self, key, value):

        value_size = 0
        if isinstance(value, (str, bytes)):
            value_size = len(value)
        elif isinstance(value, np.ndarray):
            value_size = value.size * value.dtype.itemsize
        else:
            raise ValueError("item not supported by the cache")

        if value_size > self.max_cache_size_bytes:
            raise ValueError("item too large to cache")

        while (self.size + value_size) > self.max_cache_size_bytes:
            self.remove_least_used()

        self.use_size[key] = [1, value_size]
        self.size += value_size
        self.cache_dict[key] = value

    def __getitem__(self, key):
        value = self.cache_dict[key]
        self.use_size[key][0] += 1

        return value

    def pop(self, key):
        value = self.cache_dict.pop(key)
        _, size = self.use_size.pop(key)
        self.size -= size
        return value

    def __delitem__(self, key):
        self.cache_dict.__delitem__(key)
        i = self.use_size.pop(key)
        del i

    def remove_least_used(self):
        least_used = None
        least_used_key = None
        for key, (use, _) in sorted(self.use_size.items()):
            if least_used is None:
                least_used = use
                least_used_key = key
                continue

            if use < least_used:
                least_used = use
                least_used_key = key

        if least_used_key is not None:
            x = self.pop(least_used_key)
            del x


# Module level variable. This should be used by everything so there's one and only one cache
cache = Cache()
