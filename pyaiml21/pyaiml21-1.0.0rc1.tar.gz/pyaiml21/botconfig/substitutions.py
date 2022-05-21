"""The subtitutions."""
import re
from typing import Optional, Pattern, Dict


class Substitutions:
    """
    A dict-like object that enables doing fast substitutions.

    It represents a mapping from keys to values done at once
    (without having to care about overlapping words).

    The implementation was adopted from PyAIML, the original
    AIML 1.x interpreter written in Python by Cort Stratton:

    https://github.com/cdwfs/pyaiml/blob/master/aiml/WordSub.py
    """

    def __init__(self):
        """Create the substitutions."""
        self._mapping: Dict[str, str] = {}
        self._regex: Optional[Pattern[str]] = None
        self._is_dirty_regex = False

    def _update_regex(self):
        self._is_dirty_regex = False
        self._regex = re.compile(
            "|".join(self._mapping.keys()),
            flags=re.IGNORECASE | re.UNICODE
        )

    @staticmethod
    def _prep_key(key: str) -> str:
        """We are storing all keys as lower-cased."""
        return key.casefold()

    def __getitem__(self, _name: str) -> str:
        """Get the corresponding substitution."""
        return self._mapping[self._prep_key(_name)]

    def __setitem__(self, _name: str, _value: str) -> None:
        """
        Update the substitutions.

        Map `_name` in any case to `_value` without changing its case.
        It is recommended to apply any AIML transformation afterwards to be
        sure of the resulting case.
        """
        self._mapping[self._prep_key(_name)] = _value
        self._is_dirty_regex = True

    def sub(self, text: str) -> str:
        """
        Perform the substitutions.

        Replace any substring of `text` equal to any key from
        the dictionary with the corresponding value. The replacement
        is done case-insensitive.

        :param text: text to be substituted
        :return: text with replaced substrings

        Example:
            >>> s = Substitutions()
            >>> s.sub("Nothing happens") == "Nothing happens"
            True

            >>> s["dog"] = "cat"
            >>> s["cat"] = "dog"
            >>> s["lama"] = "spaRRow"
            >>> s.sub("A dog met a lama") == "A cat met a spaRRow"
            True

            >>> s[" car "] = "bike"
            >>> s.sub("I have a car you dont") == "I have abikeyou dont"
            True
        """
        if self._is_dirty_regex:
            self._update_regex()
        if self._regex is None:
            return text
        text = f" {text} "
        return re.sub(self._regex, lambda x: self[x.group(0)], text).strip()
