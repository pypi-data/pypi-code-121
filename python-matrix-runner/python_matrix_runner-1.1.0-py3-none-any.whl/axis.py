# -*- coding: utf-8 -*-

import weakref

from typing import List, Union, Type, Iterator
from enum import Enum

from ._helper import fnmatch_ex


class Axis:
    """Build matrix axis with list of configuration values.

    An axis is one dimension of a multidimensional configuration matrix.
    Each axis (dimension) can take a fixed set of values.
    """

    _instances = set()

    def __init__(self, name: str, abbrev: str = None, values: Union[List[Enum], Type[Enum]] = None, desc: str = None):
        """Initialize a new Axis.

        Args:
            name: A unique (per Builder) Axis name.
            abbrev: A unique (per Builder) Axis abbreviation.
            values: Values that can be taken on this Axis.
            desc: Descriptive text to document the intention of this Axis.
        """
        if abbrev and len(abbrev) != 1:
            raise ValueError('Parameter abbrev must be a single character string or None')

        self._name: str = name
        self._abbrev: str = abbrev
        self._values: List[Enum] = list(values) if values else []
        self._desc: str = desc

        self._instances.add(weakref.ref(self))

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._name} at 0x{id(self):08X}>'

    def __getitem__(self, index: int) -> Enum:
        return self._values[index]

    @staticmethod
    def tostring(value: Enum, index: int = 0) -> str:
        """Convert Enum literal to string.

        Args:
            value: The Enum literal value.
            index: The nth tuple to be used, defaults to 0.
        """
        val = value.value
        if isinstance(val, tuple):
            return str(val[index])
        return str(val)

    @classmethod
    def get_instances(cls) -> Iterator:
        """Retrieve all class instances."""
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @property
    def name(self) -> str:
        """The unique name identifying this Axis."""
        return self._name

    @property
    def abbrev(self) -> str:
        """The unique abbreviation for this Axis."""
        return self._abbrev

    @property
    def values(self) -> List[Enum]:
        """Values for this matrix Axis."""
        return self._values

    @property
    def desc(self) -> str:
        """Descriptive text to document the intention of this Axis."""
        return self._desc

    def lookup(self, pattern: str) -> List[Enum]:
        """Retrieve all Axis values matching a fnmatch pattern.

        Args:
            pattern: fnmatch pattern to match values against.

        Returns:
            A list with values matching the pattern, might be empty.
        """
        result = []
        for value in self._values:
            if fnmatch_ex(value, pattern):
                result += [value]
        return result

    def converter(self):
        """Retrieve a converter function to convert patterns to values.

        Returns:
            A function of type "pattern (string) -> List of Axis values".
        """
        def convert(pattern: str) -> List[Enum]:
            """Converter function to convert patterns to values.

            Args:
                pattern (string): A fnmatch pattern.

            Returns:
                A list of Axis value matching the given pattern, may be empty.
            """
            resolved = self.lookup(pattern)
            if resolved:
                return resolved
            raise ValueError
        return convert
