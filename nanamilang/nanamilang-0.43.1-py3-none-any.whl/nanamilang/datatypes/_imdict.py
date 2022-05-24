"""NanamiLang immutable dict polyfill"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


class ImDict(dict):
    """
    Python 3 Immutable Dictionary Polyfill

    According to https://www.python.org/dev/peps/pep-0351
    """
    def __hash__(self):
        """Override a default dict.__hash__() behavior"""
        return id(self)

    @staticmethod
    def __immutable(*_, **__):
        """Prevent data mutation, immutable dictionary"""
        raise TypeError('ImDict: mutation was prevented')

    __setitem__ = __delitem__ = clear = \
        update = setdefault = pop = popitem = __immutable
