from abc import ABCMeta
from collections.abc import Sequence

from better_abc import abstract_attribute


class BaseCollection(Sequence, metaclass=ABCMeta):
    _type = abstract_attribute()

    def __init__(self, items):
        self._list = list(items)
        self._check_types()

    def _check_types(self):
        for v in self._list:
            if not isinstance(v, self._type):
                raise TypeError(v)

    def pluck(self, prop):
        """
        Get a list with the values of the given prop.

        :param str prop: Property to pluck from the scope values.
        :return:
        """
        return [getattr(v, prop) for v in self._list]
