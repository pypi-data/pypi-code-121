"""Remove puctuantion from string."""
import re
import sys
from typing import List, Union
from unicodedata import category

punctuation = "".join(
    chr(i) for i in range(sys.maxunicode) if category(chr(i)).startswith("P")
)
patt = re.compile(rf"[{re.escape(punctuation)}]")


def remove_punct(text: Union[str, List[str]]) -> Union[str, List[str]]:
    if isinstance(text, str):
        return patt.sub(" ", text)

    return [patt.sub(" ", elm) for elm in text]
