"""Nanamilang Character Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type


class Character(Base):
    """NanamiLang Character Data Type Class"""

    name = 'Character'
    _expected_type = str
    _python_reference: str
    purpose = 'Encapsulate Python 3 str (one char)'

    def format(self, **_) -> str:
        """NanamiLang Character, format() method implementation"""

        return f'\\{self._python_reference}'

    @export()
    def instance(self) -> Type:
        """NanamiLang Character, instance() method implementation"""

        return Type(self.name)

    def to_py_str(self) -> str:
        """NanamiLang Character, to_py_str() method implementation"""

        return self._python_reference
