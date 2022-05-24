"""NanamiLang HashMap Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from nanamilang import shortcuts
from ._exports import export
from ._imdict import ImDict
from .base import Base
from .collection import Collection
from .boolean import Boolean
from .string import String
from .vector import Vector


class HashMap(Collection):
    """NanamiLang HashMap Data Type Class"""

    name: str = 'HashMap'
    _expected_type = dict
    _python_reference: dict
    _default = ImDict
    purpose = 'Implements HashMap of NanamiLang Data Types'

    def _init__assertions_on_non_empty_reference(self,
                                                 reference) -> None:
        """NanamiLang HashMap, assert: raw reference coll is even"""

        self._init_assert_only_base(reference)
        self._init_assert_ref_length_must_be_even(reference)
        # make-hashmap already takes care, but we must ensure anyway

    def _init__chance_to_process_and_override(self, reference) -> dict:
        """NanamiLang HashMap, process and override HashSet reference"""

        # Here we can complete HashMap structure initialization procedure

        partitioned = shortcuts.plain2partitioned(reference)
        return ImDict({key.hashed(): (key, val) for key, val in partitioned})

    @staticmethod
    def unpack(coll) -> tuple:
        """NanamiLang HashMap, unpack Vector/HashMap items"""

        if isinstance(coll, Vector):
            items = coll.items()
            shortcuts.ASSERT_COLL_LENGTH_IS_EVEN(
                items,
                'HashMap.conj(): Vector items count not even'
            )
            return items
        if isinstance(coll, HashMap):
            return tuple() \
                if coll.empty().truthy() \
                else shortcuts.partitioned2plain(
                (k, v) for k, v in coll.reference().values())
        raise AssertionError('HashMap.conj(): only accept Vector or HashMap')

    def conj(self, items: List[Vector or 'HashMap']) -> 'HashMap':
        """NanamiLang HashMap, implements conj()"""

        return HashMap(
            HashMap.unpack(self)
            + tuple(shortcuts.partitioned2plain(map(HashMap.unpack, items))))

    def get(self, by: Base, default: Base = None) -> Base:
        """NanamiLang HashMap, get() implementation"""

        if not default:
            default = self._nil

        shortcuts.ASSERT_IS_CHILD_OF(
            by,
            Base,
            message='HashMap.get: by is not Base derived'
        )

        return shortcuts.get(self._python_reference.get(by.hashed(), ()), 1, default)

    def items(self) -> tuple:
        """NanamiLang HashMap, items() method implementation"""

        return tuple(map(Vector, self._python_reference.values()))

    @export()
    def contains(self, element: Base) -> Boolean:
        """NanamiLang HashMap, contains? method implementation"""

        return Boolean(element.hashed() in self._python_reference.keys())

    def to_py_str(self) -> str:
        """NanamiLang HashMap, to_py_str() method implementation"""

        # There is no sense to iterate over python reference values when we can just return a '{}' string
        if not self._python_reference.values():
            return '{}'
        return '{' + ', '.join([(self.wrap_string(k) if isinstance(k, String)
                                 else k.to_py_str()) +
                                ' ' +
                                (self.wrap_string(v) if isinstance(v, String)
                                 else v.to_py_str()) for k, v in self._python_reference.values()]) + '}'

    def format(self, **_) -> str:
        """NanamiLang HashMap, format() method re-implementation"""

        # There is no sense to iterate over python reference values when we can just return a '{}' string
        if not self._python_reference.values():
            return '{}'
        return '{' + f'{", ".join([f"{k.format()} {v.format()}" for k, v in self._python_reference.values()])}' + '}'
