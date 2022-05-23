from typing import Any

from ...meta.code_repr import from_init, CodeRepresentation
from .._typing import OptionsList
from ._Option import Option


class FlagOption(Option):
    """
    Option which stores True or False based on if it is provided or not.
    """
    def __init__(self,
                 *flags: str,
                 invert: bool = False,
                 help: str = ...):
        # Capture the code-representation of the option
        code_representation: CodeRepresentation = from_init(self, locals())

        # Save the invert flag
        self._invert: bool = invert

        super().__init__(code_representation,
                         *flags,
                         action="store_false" if invert else "store_true",
                         help=help)

    def _namespace_value_to_internal_value(self, namespace_value: Any) -> bool:
        return namespace_value

    def _internal_value_to_namespace_value(self, internal_value: Any) -> bool:
        return internal_value

    def _namespace_value_to_options_list(self, namespace_value: Any) -> OptionsList:
        # Flag should be present if value is True XOR invert is True
        return [self.flags[0]]

    def _validate_internal_value(self, value: Any):
        # Make sure the value is boolean
        if not isinstance(value, bool):
            raise TypeError(f"Flag options only take boolean values, not {value}")

    def _validate_namespace_value(self, namespace_value: Any):
        if not isinstance(namespace_value, bool):
            raise ValueError(f"Flag option expects boolean namespace value but got {namespace_value}")
