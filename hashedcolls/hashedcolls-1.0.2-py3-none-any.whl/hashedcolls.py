"""
Hashed collections: dict and list

Sample usage:

from hashedcolls import HashedDict
from hashedcolls import HashedList

d = HashedDict
l = HashedList

d({d({1: 1}): 1, l([1, 2, 3]): 2, (1,): 3})

"""

from functools import reduce


class Hashed:
    """
    Mixin that provides elements2hash()
    """

    @staticmethod
    def elements2hash(elements) -> int:
        """
        Return overall hash value
        :param elements: elements
        :return: overall elements hash
        """

        return reduce(lambda e, n: e + n,
                      map(hash, elements),
                      0)


class HashedList(list, Hashed):
    """
    Hashed list implementation
    """

    def __hash__(self) -> int:
        """
        Override default implementation
        :return: Hashed.elements2hash()
        """

        return self.elements2hash(self)


class HashedDict(dict, Hashed):
    """
    Hashed dictionary implementation
    """

    def __hash__(self) -> int:
        """
        Override default implementation
        :return: Hashed.elements2hash()
        """

        return self.elements2hash(self.items())
