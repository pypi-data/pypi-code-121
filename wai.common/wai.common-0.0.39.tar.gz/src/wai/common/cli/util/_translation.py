"""
Module for count-translation functionality for the CountOption class.
"""
from typing import Dict

from ...meta.code_repr import CodeRepresentable, from_init, CodeRepresentation


class TranslationTable(CodeRepresentable):
    """
    Reversible translation between integer spaces.
    """
    def __init__(self, *translated_values: int):
        # Must be at least 2 values
        if len(translated_values) < 2:
            raise ValueError("Must provide at least 2 values")

        # The translation must be reversible
        if len(set(translated_values)) != len(translated_values):
            raise ValueError("Translated values are not unique")

        self._code_representation: CodeRepresentation = from_init(self, locals())

        self._forward_translation: Dict[int, int] = {index: value for index, value in enumerate(translated_values)}
        self._reverse_translation: Dict[int, int] = {value: key for key, value in self._forward_translation.items()}

    def translate_forward(self, value: int) -> int:
        # Cap the value to the range of the forward translation
        value = min(max(0, value), len(self._forward_translation) - 1)

        return self._forward_translation[value]

    def can_translate_reverse(self, value: int) -> bool:
        """
        Whether the given value is valid under reverse translation.

        :param value:   The value to check.
        :return:        True if the value can be reverse-translated.
        """
        return value in self._reverse_translation

    def translate_reverse(self, value: int) -> int:
        # Make sure the value is translatable
        if not self.can_translate_reverse(value):
            raise ValueError(f"Value not in translation table: {value}")

        return self._reverse_translation[value]

    def code_repr(self) -> CodeRepresentation:
        return self._code_representation
