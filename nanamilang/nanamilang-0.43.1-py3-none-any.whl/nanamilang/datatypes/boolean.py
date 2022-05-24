"""NanamiLang Boolean Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type


class Boolean(Base):
    """NanamiLang Boolean Data Type"""

    name: str = 'Boolean'
    _expected_type = bool
    _python_reference: bool
    purpose = 'Encapsulate Python 3 bool'

    @export()
    def instance(self) -> Type:
        """NanamiLang Boolean, instance() method implementation"""

        return Type(Type.Boolean)

    def format(self, **_) -> str:
        """NanamiLang Boolean, format() method re-implementation"""

        return f'{"true" if self._python_reference is True else "false"}'
