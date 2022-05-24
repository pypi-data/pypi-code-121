"""NanamiLang Date Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import datetime
from ._exports import export
from .base import Base
from .type import Type


class Date(Base):
    """NanamiLang Date Data Type"""

    name: str = 'Date'
    _expected_type = datetime.datetime
    _python_reference: datetime.datetime
    purpose = 'Encapsulate Python 3 datetime.datetime class'

    @export()
    def instance(self) -> Type:
        """NanamiLang Date, instance() method implementation"""

        return Type(Type.Date)

    def format(self, **_) -> str:
        """NanamiLang Date, format() method re-implementation"""

        return f'#{self._python_reference.year}-{self._python_reference.month}-{self._python_reference.day}'
