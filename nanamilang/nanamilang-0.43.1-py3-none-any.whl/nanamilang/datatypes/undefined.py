"""NanamiLang Undefined Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type


class Undefined(Base):
    """NanamiLang Undefined Type"""

    name: str = 'Undefined'
    _expected_type = str
    _python_reference: str
    purpose = 'To mark as an undefined at parse-time'

    def format(self, **_) -> str:
        """NanamiLang Undefined, format() method implementation"""

        return 'undefined'

    def origin(self) -> str:
        """NanamiLang Undefined, origin() method implementation"""

        return self._python_reference

    @export()
    def instance(self) -> Type:
        """NanamiLang Undefined, instance() method implementation"""

        return Type(Type.Undefined)

    def reference(self) -> None:
        """NanamiLang Undefined, reference() method implementation"""

        return None

    def to_py_str(self) -> str:
        """NanamiLang Undefined, to_py_str() method implementation"""

        return ''

    # We redefine self.reference() method to return Python 3 NoneType
