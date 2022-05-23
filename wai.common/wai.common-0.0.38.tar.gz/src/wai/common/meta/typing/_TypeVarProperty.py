from typing import TypeVar

from ._get_argument_to_typevar import get_argument_to_typevar


class TypeVarProperty:
    """
    Property class which caches the dynamic type of a type-variable
    for a class.
    """
    def __init__(self, typevar: TypeVar):
        self._typevar: TypeVar = typevar
        self._base_class = None
        self._cache = {}

    def __get__(self, instance, owner):
        # Get the typevar argument if it's not cached
        if owner not in self._cache:
            self._cache[owner] = get_argument_to_typevar(owner, self._base_class, self._typevar)

        return self._cache[owner]

    def __set_name__(self, owner, name):
        # Prevents reassignment to parameterised generic base class
        if self._base_class is not None:
            return

        self._base_class = owner