from collections import OrderedDict


# cachetools's Cache classes are not so fully-featured as they appear. They are simple and work for many things,
# but respice needs access to a few access statistics as well as hidden access without influencing the current cache
# order.
class LRUCache:
    """
    A cache implementation with LRU (least recently used) strategy.
    """
    def __init__(self, maxsize):
        self._data = OrderedDict()
        self._maxsize = maxsize

    @property
    def maxsize(self):
        """
        Maximum size of the cache.
        """
        return self._maxsize

    @maxsize.setter
    def maxsize(self, value):
        while value < len(self._data):
            self._data.popitem()

        self._maxsize = value

    def __len__(self):
        """
        Returns how many elements are inside the cache.
        """
        return len(self._data)

    @property
    def full(self):
        """
        Returns `True` if the cache is filled up (`len(cache) == cache.maxsize`), else `False`.
        """
        return len(self._data) >= self._maxsize

    def __getitem__(self, key):
        """
        Returns a cache item.

        :param key:
            Key of cache item to retrieve.
        """
        self.update(key)
        return self._data[key]

    def get_stealth(self, key):
        """
        Returns a cache entry. This is a stealth operation, i.e. it returns the cache item without resetting
        its associated LRU value.

        :param key:
            Key of cache item to retrieve.
        """
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self.update(key)
        if len(self._data) > self.maxsize:
            self._data.popitem()

    def set_stealth(self, key, value):
        """
        Sets a cache entry as a stealth operation, i.e. add the key considering it is the least up-to-date one.
        If the cache is already full, this is a no-op.
        """
        if not self.full:
            self._data[key] = value

    def __delitem__(self, key):
        """
        Deletes a cache entry.
        """
        del self._data[key]

    def update(self, key):
        """
        Resets the LRU value of a cache entry.
        """
        self._data.move_to_end(key, last=False)

    def __iter__(self):
        """
        Iterator over all cache entry keys.
        """
        return iter(self._data.keys())

    def last(self):
        """
        Returns the last used cache entry.
        """
        try:
            return next(iter(self._data.items()))
        except StopIteration:
            raise KeyError('cache is empty') from None

    def __contains__(self, key):
        return key in self._data

    def keys(self):
        """
        Retrieves all keys inside the cache in order of last usage.

        This is a stealth operation, i.e. iterating over the cache entries **will not** change their order in the cache.
        To do so, call `update(key)` appropriately. However note, that this cannot be done from within iterating, as
        it changes the underlying data structure. To still do so raises an error.
        """
        return self.__iter__()

    def values(self):
        """
        Retrieves all values inside the cache in order of last usage.

        This is a stealth operation, i.e. iterating over the cache entries **will not** change their order in the cache.
        To do so, call `update(key)` appropriately. However note, that this cannot be done from within iterating, as
        it changes the underlying data structure. To still do so raises an error.
        """
        return iter(self._data.values())

    def items(self):
        """
        Retrieves all items (key-value pairs) inside the cache in order of last usage.

        This is a stealth operation, i.e. iterating over the cache entries **will not** change their order in the cache.
        To do so, call `update(key)` appropriately. However note, that this cannot be done from within iterating, as
        it changes the underlying data structure. To still do so raises an error.
        """
        return iter(self._data.items())

    def clear(self):
        """
        Empties the cache.
        """
        self._data.clear()

    def __repr__(self):
        return f'<{type(self).__name__} at {hex(id(self))} (capacity: {len(self._data)}/{self._maxsize} used)>'
