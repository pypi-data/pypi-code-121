"""Define de2en."""
import copy
from typing import List, Union

from logzero import logger

from de2en.d2e import d2e


def de2en(
    text: Union[str, List[List[str]]],
) -> List[str]:
    """Define de2en."""
    res = copy.deepcopy(text)
    if isinstance(text, str):
        res = [text.split()]

    try:
        res = [" ".join([d2e(word) for word in line]) for line in res]
    except Exception as exc:
        logger.error(exc)
        raise
    return res
