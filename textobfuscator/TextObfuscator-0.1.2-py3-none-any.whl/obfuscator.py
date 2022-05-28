import re
from typing import Dict, List, Pattern, Tuple

from textobfuscator.processor import (
    KEY_PREFIX,
    RULE_FUNC,
    BreakWord,
    ObfuscationConfig,
    ObfuscatorFormat,
    ObfuscatorReplace,
    ObfuscatorWordBreak,
    Replace,
)
from textobfuscator.utils import Utils

RE_KEY_ARGS = re.compile(r"(\{.*?})")
KEY_ARG_POSITION = List[Tuple[str, Tuple[int, int]]]


class TextObfuscator:
    def __init__(
        self,
        replace_source_map: Tuple[List[str], ...],
        replace_first: bool = False,
        replace_skip_items: List[Pattern] = None,
        format_prefix_rules: Dict[KEY_PREFIX, RULE_FUNC] = None,
    ):
        self.break_processor = ObfuscatorWordBreak()
        self.format_processor = ObfuscatorFormat(prefix_rules=format_prefix_rules)
        self.replace_processor = ObfuscatorReplace(
            source_map=replace_source_map,
            only_first=replace_first,
            skip_items=replace_skip_items,
        )

    @staticmethod
    def _put_back_key_args(content: str, arg_positions: KEY_ARG_POSITION) -> str:
        content_items = list(content)
        for arg, (start, end) in arg_positions:
            content_items[start:end] = arg
        return "".join(content_items)

    def break_word(self, content: str, break_words: List[BreakWord] = None) -> str:
        """Break the words according to the config."""
        if not break_words:
            return content
        return self.break_processor.mix(content, break_words)

    def replace(self, content: str, replace_config: Replace) -> str:
        """Replace the char in content according to the config."""
        if not replace_config:
            return content
        return self.replace_processor.mix(content, replace_config)

    def format(self, content: str, **kwargs) -> str:
        """Format the content, fill predefine args."""
        return self.format_processor.mix(content, **kwargs)

    def obfuscate(self, content: str, config: ObfuscationConfig, **kwargs) -> str:
        """Obfuscate the content with the config.

        1. Split content into segments by every args position.
        2. Break words.
          2.1 Break words on each segment.
          2.2 Merge all segments and all key args.
        3. Replace.
          3.1 Remove all key args.
          3.2 Mix replace.
          3.2 Put back all key args.
        """
        _, args_positions = Utils.extra_args(RE_KEY_ARGS, content)
        prev_start = 0
        content_segments = []
        for idx, (key, position) in enumerate(args_positions):
            this_end, next_start = position
            break_word = self.break_word(content[prev_start:this_end], config.break_words)
            content_segments.extend([break_word, key])
            prev_start = next_start
        else:
            break_word = self.break_word(content[prev_start:], config.break_words)
            content_segments.append(break_word)
        breaded_content = "".join(content_segments)

        _content, args_positions = Utils.extra_args(RE_KEY_ARGS, breaded_content)
        replaced_content = self.replace(_content, config.replaces)
        need_format_content = self._put_back_key_args(replaced_content, args_positions)

        # Insert args if we have, or leave it as is.
        return self.format(need_format_content, **kwargs)
