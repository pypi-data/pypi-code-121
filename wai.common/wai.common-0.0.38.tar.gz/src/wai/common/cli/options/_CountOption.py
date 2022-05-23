from typing import Optional, Any

from ...meta.code_repr import CodeRepresentation, from_init
from ..constants import SHORT_FLAG_PREFIX
from ..util import is_short_flag, TranslationTable
from .._typing import OptionsList
from ._Option import Option


class CountOption(Option):
    """
    Option which counts the number of times its flag appears.

    Can optionally supply a translation table to translate from
    actual count values to some other set of integers (e.g. from
    counts to verbosity values).
    """
    def __init__(self,
                 *flags: str,
                 translation: Optional[TranslationTable] = None,
                 help: str = ...):
        # Capture the code-representation of the option
        code_representation: CodeRepresentation = from_init(self, locals())

        # Create the translation pair
        self._translation: Optional[TranslationTable] = translation

        super().__init__(code_representation,
                         *flags,
                         action="count",
                         default=0,
                         help=help)

    def _namespace_value_to_internal_value(self, namespace_value: Any) -> int:
        return (
            self._translation.translate_forward(namespace_value)
            if self._translation is not None
            else namespace_value
        )

    def _internal_value_to_namespace_value(self, value: Any) -> int:
        return (
            self._translation.translate_reverse(value)
            if self._translation is not None
            else value
        )

    def _namespace_value_to_options_list(self, namespace_value: Any) -> OptionsList:
        # Try to use a short flag if available, otherwise just the first flag
        selected_flag = self.flags[0]
        short_flag = is_short_flag(selected_flag)
        if len(self.flags) == 2 and not short_flag:
            selected_flag = self.flags[1]
            short_flag = True

        # Iterate the flag count times
        if short_flag:
            return [SHORT_FLAG_PREFIX + selected_flag[1] * namespace_value]
        else:
            return [selected_flag] * namespace_value

    def _validate_internal_value(self, internal_value: Any):
        # Value must be an integer
        if not isinstance(internal_value, int):
            raise TypeError(f"Count options take integer values, not {internal_value}")

        # Value must be reverse-translatable if we have a translation
        if self._translation is not None and not self._translation.can_translate_reverse(internal_value):
            raise ValueError(f"Value {internal_value} is not valid for the translation table")

    def _validate_namespace_value(self, namespace_value: Any):
        # Namespace values are integers
        if not isinstance(namespace_value, int):
            raise TypeError(f"Count options expect integer namespace values, not {namespace_value}")

        # Must be at least 0 (can't have negative count)
        if namespace_value < 0:
            raise ValueError(f"Can't have negative count ({namespace_value})")
