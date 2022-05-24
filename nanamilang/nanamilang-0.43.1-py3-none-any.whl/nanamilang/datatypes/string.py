"""NanamiLang String Data Type CLass"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import get
from ._exports import export
from .base import Base
from .type import Type
from .nil import Nil
from .boolean import Boolean
from .integernumber import IntegerNumber
from .keyword import Keyword
from .character import Character


class String(Base):
    """NanamiLang String Data Type"""

    name: str = 'String'
    _expected_type = str
    _python_reference: str
    __reference_helpers = (0, '',)
    purpose = 'Encapsulate Python 3 str'

    def truthy(self) -> bool:
        """NanamiLang String, truthy() method implementation"""

        return True

    def format(self, **_) -> str:
        """NanamiLang String, format() method implementation"""

        return f'"{self._python_reference}"'

    @export()
    def instance(self) -> Type:
        """NanamiLang String, instance() method implementation"""

        return Type(Type.String)

    def to_py_str(self) -> str:
        """NanamiLang String, to_py_str() method implementation"""

        return self._python_reference

    @export()
    def replace(self, pattern: Base, replacement: Base) -> Base:
        """Nanamilang String, replace() method implementation"""

        assert isinstance(pattern, String), (
            'String.replace(): pattern needs to be a String'
        )
        assert isinstance(replacement, String), (
            'String.replace(): replacement needs to be a String'
        )
        return String(
            self.reference().replace(
                pattern.reference(),   replacement.reference()))

    @export()
    def keyword(self) -> Keyword:
        """NanamiLang String, cast self(String) into a Keyword"""

        return Keyword(self.reference())  # <----- that simple :)

    def get(self,
            index: IntegerNumber,
            default: Base = None) -> Base:
        """NanamiLang String, get() method implementation"""

        assert isinstance(index, IntegerNumber), (
            'String.get(): idx should be IntegerNumber'
        )
        default = default or Nil('nil')
        assert isinstance(default, (String, Nil)), (
            'String.get(): default should be a String or Nil'
        )
        item = get(self.reference(), index.reference(), default)
        return String(item) if isinstance(item, str) else default

    @export()
    def count(self) -> IntegerNumber:
        """NanamiLang String, count() method implementation"""

        return IntegerNumber(self.reference().__len__())

    @export()
    def empty(self) -> Boolean:
        """NanamiLang String, empty() method implementation"""

        return Boolean(len(self.reference()) == 0)

    def items(self) -> tuple:
        """NanamiLang String, items() method implementation"""

        return tuple(map(Character, self.reference()))

    @export()
    def contains(self, comparable: Base) -> Boolean:
        """NanamiLang String, contains() method implementation"""

        assert isinstance(comparable, String), (
            'String.contains():  comparable needs to be a String'
        )
        return Boolean(comparable.reference() in self.reference())

    def reference(self) -> str:
        """NanamiLang String, reference() method implementation"""

        idx, retval = self.__reference_helpers

        while idx < len(self._python_reference):
            if self._python_reference[idx] == '\\':
                idx += 1
                escaped = self._python_reference[idx]
                # TODO:: handle more escape sequences
                if escaped == '"':
                    retval += '"'   # string boundary
                if escaped == 'n':
                    retval += '\n'  # a new-line char
                if escaped == "/":
                    retval += "/"   # /  pass-through
                # Leave an escape seq as is otherwise
                idx += 1
            else:
                retval += self._python_reference[idx]
                idx += 1

        return retval

    # We redefine self.reference() to handle the escape sequences
    # We redefine self.truthy() to validate empty strings as well
