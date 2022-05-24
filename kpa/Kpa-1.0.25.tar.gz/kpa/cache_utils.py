
class lru_cache_set:
    '''
    A set that is limited to size `maxsize` by removing the least-recently-accessed item when necessary.
    `.add()`ing an item that is already present simply updates the access time for that item.
    Checking `item in cache` updates the access time for that item.

    Items must be `hash()`able.

    It is implemented with a dict and a circular-doubly-linked-list of items, sorted by how recently they were accessed.
    '''
    OLDER, NEWER, KEY = 0, 1, 2

    def __init__(self, maxsize):
        self.maxsize = maxsize; assert maxsize >= 2
        self._cache = {} # like `{<key> -> <item>}`
        # <item> is like [<older>, <newer>, <key>] (where older & newer are like <item>)
        # self._root is a special <item>:
        # self._root[OLDER] is the newest item, and self._root[NEWER] is the oldest.
        self._root = []; self._root[:] = [self._root, self._root, None]

    def __repr__(self):
        keys = []
        item = self._root[self.NEWER]
        while item is not self._root:
            assert item[self.NEWER][self.OLDER] is item
            keys.append(item[self.KEY])
            item = item[self.NEWER]
        return repr(keys)

    def __contains__(self, key):
        # checks whether we contain a key and also makes it the newest
        item = self._cache.get(key, None)
        if item is None:
            return False
        self._move_item_to_newest(item)
        return True

    def add(self, key):
        # add a key.  if we already have it, just make it newest.
        NEWER, OLDER, KEY = self.NEWER, self.OLDER, self.KEY
        if key in self._cache:
            self._move_item_to_newest(self._cache[key])

        else:
            if len(self._cache) == self.maxsize:
                # re-use item that used to be oldest
                item = self._root[NEWER]
                del self._cache[item[KEY]]
                # splice it out
                item[OLDER][NEWER] = item[NEWER]
                item[NEWER][OLDER] = item[OLDER]
                item[:] = [self._root[OLDER], self._root, key]
            else:
                item = [self._root[OLDER], self._root, key]
            self._cache[key] = item
            self._root[OLDER][NEWER] = item
            self._root[OLDER] = item

    def _move_item_to_newest(self, item):
        OLDER, NEWER = self.OLDER, self.NEWER
        if item is self._root[OLDER]: return
        # splice out item
        item[OLDER][NEWER] = item[NEWER]
        item[NEWER][OLDER] = item[OLDER]
        # splice in item as newest
        item[OLDER] = self._root[OLDER]
        item[NEWER] = self._root
        self._root[OLDER][NEWER] = item
        self._root[OLDER] = item
        self._root[OLDER] = item


class _lru_cache_set_slow:
    'a simple but inefficient implementation of lru_cache_set'
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self._keys = [] # oldest item is at self._keys[0], newest is at self._keys[-1]
    def __repr__(self):
        return repr(self._keys)
    def add(self, key):
        if key in self._keys:
            self._keys.remove(key)
        self._keys.append(key)
        if len(self._keys) > self.maxsize:
            self._keys.pop(0)
    def __contains__(self, key):
        if key not in self._keys:
            return False
        self._keys.remove(key)
        self._keys.append(key)
        return True


if __name__ == '__main__':

    c1 = lru_cache_set(4)
    c2 = _lru_cache_set_slow(4)
    assert repr(c1) == repr(c2)
    for key in 'b b a b c d e b d b f a b c d'.split():
        c1.add(key)
        c2.add(key)
        print(key, c1)
        assert repr(c1) == repr(c2)

    for key in 'abcdefg':
        has1 = key in c1
        has2 = key in c2
        assert has1 == has2, (key, has1, has2, c1, c2)
        assert repr(c1) == repr(c2)
        print('{}{}{}'.format('-+'[int(has1)], key, c1))
