"""NanamiLang HashSet Data Type Class"""

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


class HashSet(Collection):
    """NanamiLang HashSet Data Type Class"""

    name: str = 'HashSet'
    _expected_type = dict
    _python_reference: dict
    _default = ImDict
    purpose = 'Implements HashSet of NanamiLang Data Types'

    def _init__chance_to_process_and_override(self, reference) -> dict:
        """NanamiLang HashSet, process and override HashMap reference"""

        # Here we can complete HashSet structure initialization procedure

        return ImDict({element.hashed(): element for element in reference})

    def conj(self, items: List[Base]) -> 'HashSet':
        """NanamiLang HashSet, implements conj()"""

        return HashSet(self.items() + tuple(items))

    def get(self, by: Base, default: Base = None) -> Base:
        """NanamiLang HashSet, get() implementation"""

        if not default:
            default = self._nil

        shortcuts.ASSERT_IS_CHILD_OF(
            by,
            Base,
            message='HashSet.get: by is not Base derived'
        )

        return self._python_reference.get(by.hashed(), default)

    def items(self) -> tuple:
        """NanamiLang HashSet, items() method implementation"""

        return tuple(self._python_reference.values())

    @export()
    def contains(self, element: Base) -> Boolean:
        """NanamiLang HashSet, contains? method implementation"""

        return Boolean(element.hashed() in self._python_reference.keys())

    def to_py_str(self) -> str:
        """NanamiLang HashSet, to_py_str() method implementation"""

        # There is no sense to iterate over python reference values when we can just return a '#{}'
        if not self._python_reference.values():
            return '#{}'
        return '#{' + ' '.join([self.wrap_string(i) if isinstance(i, String)
                                else i.to_py_str() for i in self._python_reference.values()]) + '}'

    def format(self, **_) -> str:
        """NanamiLang HashSet, format() method re-implementation"""

        # There is no sense to iterate over python reference values when we can just return a '#{}'
        if not self._python_reference.values():
            return '#{}'
        return '#{' + f'{" ".join((item.format() for item in self._python_reference.values()))}' + '}'
