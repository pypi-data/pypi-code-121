"""NanamiLang Function Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from .callable import Callable


class Function(Callable):
    """NanamiLang Function Data Type Class"""

    name: str = 'Function'
    purpose = 'Encapsulate Function name and Python 3 handle'

    def _additional_assertions_on_init(self,
                                       reference) -> None:
        """NanamiLang Function, verify Function description"""

        self._init_assert_reference_has_keys(
            reference, {'function_name', 'function_reference'}
        )

    def _set_hash(self, reference) -> None:
        """NanamiLang Function, overridden Base '_set_hash()'"""

        self._hashed = hash(reference.get('function_reference'))

    def format(self, **_) -> str:
        """NanamiLang Function, format() method implementation"""

        return self._python_reference.get('function_name')

    def reference(self):
        """NanamiLang Function, reference() method implementation"""

        return self._python_reference.get('function_reference')

    # format() and reference() return function name and handle respectively
    # Since self._python_reference is a dict of function name and reference
