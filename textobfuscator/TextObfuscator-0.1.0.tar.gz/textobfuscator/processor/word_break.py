import random
import re
from typing import Dict, List

from ..utils import Utils
from .construct import BaseObscure, BreakWord

RE_BREAK_CHECK_SPLITTER = re.compile(r"\w+")


class ObfuscatorWordBreak(BaseObscure):
    @staticmethod
    def break_word(word: str, config: BreakWord) -> str:
        """Break a word according to the config.

        Break a word into serval parts, and insert a separator between them.
        Eg: "hello" -> "he[SPLITER]l[SPLITER]lo"
            "verification" -> "ver[SPLITER]ifi[SPLITER]cat[SPLITER]ion"
        [SPLITER] can be any separator you need, like ",", "|", " ", ":".
        """
        # Keep break place inside the word, otherwise it looks no break.
        max_break_times = len(word) - 1
        break_times = min(config.places, max_break_times)
        break_positions = random.sample(range(max_break_times), break_times)
        new_set = []
        for idx, letter in enumerate(word):
            new_set.append(letter)
            if idx in break_positions:
                new_set.append(config.fill)
        return "".join(new_set)

    def mix(self, content: str, break_words: List[BreakWord]) -> str:
        """Break special words in content according to break_words config."""
        upper_break_map: Dict[str, BreakWord] = {w.word.upper(): w for w in break_words}

        _, args_positions = Utils.extra_args(RE_BREAK_CHECK_SPLITTER, content)
        prev_start = 0
        new_words_set = []
        for idx, (key, position) in enumerate(args_positions):
            this_end, next_start = position
            word_unit = key
            _config = upper_break_map.get(key.upper())
            if _config and (not _config.sensitive or _config.word == key):
                word_unit = self.break_word(key, _config)
            new_words_set.extend([content[prev_start:this_end], word_unit])
            prev_start = next_start
        else:
            new_words_set.append(content[prev_start:])
        return "".join(new_words_set)
