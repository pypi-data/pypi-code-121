import random
import string
from typing import Dict, List, Tuple

from textobfuscator.processor import KEY_PREFIX, RULE_FUNC, ObfuscatorReplace
from textobfuscator.utils import ChoiceEnum

from .replace_maps import MAP_CYRILLIC_MIX_SOURCE, MAP_MIX_SOURCE, MAP_SIMPLE_MIX_SOURCE


class TextObfuscatorReplaceLevel(ChoiceEnum):
    L1 = "L1", (MAP_MIX_SOURCE, False)
    L2 = "L2", (MAP_SIMPLE_MIX_SOURCE, False)
    L3 = "L3", (MAP_CYRILLIC_MIX_SOURCE, True)

    def __init__(self, key, replace_mapping: Tuple[Tuple[List], bool]):
        self.key = key
        self.mapping, self.only_first = replace_mapping

    @property
    def processor(self):
        """Get the processor for this level."""
        return ObfuscatorReplace(self.mapping, only_first=self.only_first)


class ObfuscatorFormatPrefixRules:
    @property
    def _punctuations(self):
        # Remove potentially ambiguous characters.
        excluded = ["{", "}", "\\"]
        return [i for i in string.punctuation if i not in excluded]

    @property
    def rules(self) -> Dict[KEY_PREFIX, RULE_FUNC]:
        """Give the users the default rules we provide."""
        return {
            "digit": lambda: random.choice(string.digits),
            "letter": lambda: random.choice(string.ascii_letters),
            "symbol": lambda: random.choice(self._punctuations),
        }


DEFAULT_FORMAT_PREFIX_RULES = ObfuscatorFormatPrefixRules().rules
