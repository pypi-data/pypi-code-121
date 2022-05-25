"""Translate english to chinese via a dict."""
import copy
from typing import List, Union

# from word_tr import word_tr
from .json_de2zh import json_de2zh


# fmt: off
def de2zh(
        text: Union[str, List[List[str]]],
) -> List[str]:
    # fmt: on
    """Translate english to chinese via a dict.

    Args
        text: to translate, list of list of str

    Returns
        res: list of str
    """
    res = copy.deepcopy(text)
    if isinstance(text, str):
        res = [text.split()]

    # if res and isinstance(res[0], str):
        # res = [line.lower().split() for line in res]

    res = ["".join([json_de2zh(word) for word in line]) for line in res]

    return res
