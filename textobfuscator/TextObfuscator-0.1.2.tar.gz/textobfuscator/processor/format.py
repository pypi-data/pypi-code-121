from collections import defaultdict
from itertools import chain
from typing import Callable, Dict, List

from textobfuscator.utils import FullFillFormat, Utils

from .construct import BaseObfuscator

KEY_PREFIX = str
RULE_FUNC = Callable[[], str]


class ObfuscatorFormat(BaseObfuscator):
    def __init__(self, prefix_rules: Dict[KEY_PREFIX, RULE_FUNC] = None):
        self.prefix_rules = prefix_rules or {}

    def get_prefill_args(self, args_names: List[str]) -> Dict:
        """Generate value for each args_names if them matched one of `prefix_rules`.

        Same arg_name will be the same value.
        Examples(if we have a random digit func on `prefix_rules` for prefix: digit)
            ['digit1', 'digit3', 'digit1'] -> {'digit1': 8, 'digit3': 2}

        """
        if not self.prefix_rules:
            return {}
        args_map = defaultdict(dict)
        predefined_arg_prefix = tuple(self.prefix_rules.keys())
        for arg_name in args_names:
            if not arg_name.startswith(predefined_arg_prefix):
                continue
            for prefix, rule_func in self.prefix_rules.items():
                if not arg_name.startswith(prefix) or arg_name in args_map[prefix]:
                    continue
                args_map[prefix][arg_name] = rule_func()
        return dict(chain(*[i.items() for i in args_map.values()]))

    def mix(self, content: str, **kwargs) -> str:
        """Format all args that we can get it, and keep the original if we can't."""
        args_names = Utils.get_arg_keys(content)
        # Not find args need format.
        if not args_names:
            return content
        prefill_args = self.get_prefill_args(args_names)
        return content.format_map(FullFillFormat(**prefill_args, **kwargs))
