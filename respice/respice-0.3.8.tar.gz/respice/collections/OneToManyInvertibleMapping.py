from collections.abc import MutableMapping

from ordered_set import OrderedSet


class OneToManyInvertibleMapping(MutableMapping):
    """
    A one-to-many mapping structure maintaining insertion order for values with fast reverse lookup.
    """

    class _ReverseDict(MutableMapping):
        def __init__(self, obverse):
            self._obverse = obverse
            self._reverse = dict()

        @property
        def obverse(self):
            return self._obverse

        def keys(self):
            return self._reverse.keys()

        def values(self):
            return self._reverse.values()

        def items(self):
            return self._reverse.items()

        def __getitem__(self, key):
            return self._reverse[key]

        def __setitem__(self, key, value):
            if key in self._reverse:
                if self._reverse[key] is value:
                    return

                raise ValueError('value is already obversely mapped to a different key - '
                                 'if you want to reset the relation, first delete key from value in the obverse '
                                 'mapping')

            self._reverse[key] = value

            if value in self._obverse._obverse:
                obverse_set = self._obverse[value]
            else:
                obverse_set = OrderedSet()
                self._obverse._obverse[value] = obverse_set

            obverse_set.add(key)

        def __delitem__(self, key):
            value = self._reverse[key]
            del self._reverse[key]

            obverse_set = self._obverse._obverse[value]
            obverse_set.remove(key)
            if not obverse_set:
                del self._obverse._obverse[value]

        def __iter__(self):
            return iter(self._reverse)

        def __len__(self):
            return len(self._reverse)

        def __repr__(self):
            return repr(self._reverse)

    def __init__(self, initialdata=None):
        self._obverse = dict()
        self._reverse = self._ReverseDict(self)

        if initialdata is not None:
            if isinstance(initialdata, OneToManyInvertibleMapping):
                for k, vs in initialdata.items():
                    for v in vs:
                        self.__setitem__(k, v)

            elif isinstance(initialdata, dict):
                for k, v in initialdata.items():
                    self.__setitem__(k, v)
            else:
                raise TypeError

    @property
    def reverse(self):
        return self._reverse

    def keys(self):
        return self._obverse.keys()

    def values(self):
        return self._obverse.values()

    def items(self):
        return self._obverse.items()

    def __getitem__(self, key):
        return self._obverse[key].copy()

    def __setitem__(self, key, value):
        if key in self._obverse:
            obverse_set = self._obverse[key]
        else:
            obverse_set = OrderedSet()
            self._obverse[key] = obverse_set

        obverse_set.add(value)

        self._reverse._reverse[value] = key

    def __delitem__(self, key):
        obverse_set = self._obverse[key]
        del self._obverse[key]

        for reverse in obverse_set:
            del self._reverse._reverse[reverse]

    def __iter__(self):
        return iter(self._obverse)

    def __len__(self):
        return len(self._obverse)

    def __repr__(self):
        return repr(self._obverse)
