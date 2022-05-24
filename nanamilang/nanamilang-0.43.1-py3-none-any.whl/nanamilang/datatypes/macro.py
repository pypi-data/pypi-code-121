"""NanamiLang Macro Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from .callable import Callable


class Macro(Callable):
    """NanamiLang Macro Data Type Class"""

    name: str = 'Macro'
    purpose = 'Encapsulate Macro name and Python 3 handle'

    def _additional_assertions_on_init(self,
                                       reference) -> None:
        """NanamiLang Macro, verify Macro description"""

        self._init_assert_reference_has_keys(
            reference, {'macro_name', 'macro_reference'}
        )

    def _set_hash(self, reference) -> None:
        """NanamiLang Macro, overridden Base '_set_hash()'"""

        self._hashed = hash(reference.get('macro_reference'))

    def format(self, **_) -> str:
        """NanamiLang Macro, format() method implementation"""

        return self._python_reference.get('macro_name')

    def reference(self):
        """NanamiLang Macro, reference() method implementation"""

        return self._python_reference.get('macro_reference')

    # format() and reference() return macro name and handle respectively
    # Since self._python_reference is a dict of macro name and reference
