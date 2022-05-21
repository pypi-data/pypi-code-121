from typing import TypeVar, Set

from pkm.utils.types import Hashable

_T = TypeVar("_T", bound=Hashable)


def try_add(st: Set[_T], item: _T) -> bool:
    """
    tries to add an item to the set indicating if the operation succeeded
    :param st: the set to add the item into
    :param item: the item to add
    :return: True if it was added, False if it was already in the set
    """

    ln = len(st)
    st.add(item)
    return ln != len(st)
