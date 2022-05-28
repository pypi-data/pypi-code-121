import random
import re
from typing import Dict, List, Pattern, Tuple

from ..utils import Utils
from .construct import BaseObfuscator, Replace

DEFAULT_SKIP_ITEMS: List[Pattern] = [
    # Url.
    re.compile(r"(\bhttps?://\S+)|(\S*[a-zA-Z\d]+\.[a-zA-Z]{1,10}/\S*)"),
    # Phone number.
    re.compile(r"\d{8,}"),
    # Verification code.
    re.compile(r"\d{4,}"),
]


class ObfuscatorReplace(BaseObfuscator):
    def __init__(self, source_map: Tuple[List, ...], only_first: bool = False, skip_items: List[Pattern] = None):
        self._map, self._pattern = self.build_similar_map(source_map, only_first)
        self.skip_re_items = DEFAULT_SKIP_ITEMS if skip_items is None else skip_items

    @staticmethod
    def build_similar_map(source: Tuple[List, ...], only_first: bool = False) -> Tuple[Dict, Pattern]:
        """Build mapping/regex for each char we want to replace according to the source map.

        For each group chars in source:
        1. We make a mapping for each char in the group to this group(this group also as candidate chars),
           if `only_first` is True, we only build for the first one char in the every group.
        2. And we make a regex for all chars we need to replace in the content.

        Args
            source: Groups of chars we want to replace, eg: (['a', '0', 'O'], ['@', '#', '$'])
            only_first: Build mapping only for the first one char in every group or not.

        Returns
            A tuple of mapping and regex.

        """
        line_mix_position = 1 if only_first else None
        _map = {char: chars.copy() for chars in source for char in chars[:line_mix_position]}
        # Remove self item.
        for char, similar_chars in _map.items():
            similar_chars.remove(char)

        pattern = "".join(_map.keys())
        return _map, re.compile("[%s]" % pattern)

    def remove_skip_items(self, content: str) -> str:
        """Remove skip items from the content."""
        for item_re in self.skip_re_items:
            content, _ = Utils.extra_args(item_re, content)
        return content

    @staticmethod
    def calc_replace_cnt(matched_cnt: int, replace_config: Replace) -> int:
        """Calc the replaces count that we need."""
        config_replace_cnt = 0
        if replace_config.count is not None:
            config_replace_cnt = replace_config.count
        elif replace_config.percent is not None:
            config_replace_cnt = int(matched_cnt * replace_config.percent / 100)
        elif replace_config.remaining is not None:
            config_replace_cnt = max(matched_cnt - replace_config.remaining, 0)
        return min(matched_cnt, config_replace_cnt)

    def mix(self, content, config: Replace) -> str:
        """Replace char on the content according to the config and source map.

        1. Ignore the skip items(can be searched by the `skip_items` regex you specify during init).
        2. Randomly choose a char from the source map to replace the matched char as we need.
        3. Put back skip items and combine with replaced chars to return.
        """
        cleaned_content = self.remove_skip_items(content)
        matched_places = list(self._pattern.finditer(cleaned_content))
        replace_cnt = self.calc_replace_cnt(len(matched_places), config)

        for match in random.sample(matched_places, replace_cnt):
            start, end = match.start(), match.end()
            substitutes = self._map[match.group(0)]
            replace_with = random.choice(substitutes)
            content = f"{content[:start]}{replace_with}{content[end:]}"
        return content
