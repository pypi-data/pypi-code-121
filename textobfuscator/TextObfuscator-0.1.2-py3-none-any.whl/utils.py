import string
from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from typing import List, Pattern, Tuple

STR_FORMATTER = string.Formatter()
KEY_ARG_POSITION = List[Tuple[str, Tuple[int, int]]]


class ChoiceEnum(Enum):
    ...


@dataclass
class BaseDataclass:
    ...


class FullFillFormat(UserDict):
    def __missing__(self, key):
        """Keep the original holder if we don't have the arg value."""
        return "{" + key + "}"


class Utils:
    @staticmethod
    def get_arg_keys(template) -> List[str]:
        """Get key args names from string."""
        return [i[1] for i in STR_FORMATTER.parse(template) if i[1] is not None]

    @staticmethod
    def extra_args(re_extract: Pattern, content: str) -> Tuple[str, KEY_ARG_POSITION]:
        """Split key args from content."""
        arg_positions = []
        content_items = list(content)
        for arg in re_extract.finditer(content):
            arg_positions.append((arg.group(), arg.span()))
            content_items[arg.start() : arg.end()] = " " * (arg.end() - arg.start())
        return "".join(content_items), arg_positions

    @staticmethod
    def put_back_key_args(content: str, arg_positions: KEY_ARG_POSITION) -> str:
        """Put back the args to the content according to the arg_positions that we calc before."""
        content_items = list(content)
        for arg, (start, end) in arg_positions:
            content_items[start:end] = arg
        return "".join(content_items)
