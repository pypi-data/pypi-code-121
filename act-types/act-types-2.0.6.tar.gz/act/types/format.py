import re
from typing import Text


def default_lowercase_format(value: Text) -> Text:
    """Default lowercase format
    * remove text in paranthesis
    * replace multiple whitespace with single space
    * lowercase
    """

    return re.sub(r"\s+", " ", re.sub(r"\(.*\)", "", str(value))).lower().strip()


OBJECT_FORMATTERS = {
    "tool": default_lowercase_format,
    "threatActor": default_lowercase_format,
}


def object_format(object_type: Text, object_value: Text) -> Text:
    if object_type in OBJECT_FORMATTERS:
        return OBJECT_FORMATTERS[object_type](object_value)

    # No formatter specified
    return object_value
