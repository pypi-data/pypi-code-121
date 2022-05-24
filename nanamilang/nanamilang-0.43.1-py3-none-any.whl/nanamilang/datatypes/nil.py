"""NanamiLang Nil Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type


class Nil(Base):
    """NanamiLang Nil Type"""

    name: str = 'Nil'
    _expected_type = str
    _python_reference: str
    purpose = 'To mark as a nil'

    def format(self, **_) -> str:
        """NanamiLang Nil, format() method implementation"""

        return 'nil'

    def origin(self) -> str:
        """NanamiLang Nil, origin() method implementation"""

        return self._python_reference

    @export()
    def instance(self) -> Type:
        """NanamiLang Nil, instance() method implementation"""

        return Type(Type.Nil)

    def reference(self) -> None:
        """NanamiLang Nil, reference() method implementation"""

        return None

    def to_py_str(self) -> str:
        """NanamiLang Nil, to_py_str() method implementation"""

        return ''

    # We redefine self.reference() method to return Python 3 NoneType
