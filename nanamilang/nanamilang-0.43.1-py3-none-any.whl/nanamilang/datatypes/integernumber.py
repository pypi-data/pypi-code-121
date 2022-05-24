"""NanamiLang IntegerNumber Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from .numeric import Numeric


class IntegerNumber(Numeric):
    """NanamiLang IntegerNumber Type"""

    name: str = 'IntegerNumber'
    _expected_type = int
    _python_reference: int
    purpose = 'Encapsulate Python 3 int'

    def truthy(self) -> bool:
        """NanamiLang IntegerNumber, truthy() method implementation"""

        return True
        # We redefine self.truthy() to always return True for all ints
