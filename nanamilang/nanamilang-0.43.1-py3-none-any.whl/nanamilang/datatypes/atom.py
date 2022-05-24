"""Nanamilang Atom Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type


class Atom(Base):
    """NanamiLang Atom Data Type Class"""

    name = 'Atom'
    _expected_type = Base
    _python_reference: Base
    purpose = 'Clojure-like atom data type'

    @export()
    def instance(self) -> Type:
        """NanamiLang Atom, instance() method implementation"""

        return Type(self.name)
