from typing import TypeVar, Callable, Iterable, Sequence, Optional, Any, List

from pkm.utils.types import Hashable, HasLessThan, StackLike

_T = TypeVar("_T")
_U = TypeVar("_U")
_K = TypeVar("_K", bound=Hashable)


def subiter(sq: Sequence[_T], offset: int = 0, length: Optional[int] = None) -> Iterable[_T]:
    if length is None:
        length = len(sq) - offset

    for i in range(offset, offset + length):
        yield sq[i]


def startswith(sq: Sequence[_T], prefix: Sequence[_T]) -> bool:
    if len(prefix) > len(sq):
        return False

    return all(s == p for s, p in zip(sq, prefix))


def argmin(seq: Sequence[_T], key: Optional[Callable[[_T], HasLessThan]]) -> int:
    if key is None:
        okey = seq.__getitem__
    else:
        def okey(i: int):
            return key(seq[i])

    return min(range(len(seq)), key=okey)


def argmax(seq: Sequence[_T], key: Optional[Callable[[_T], HasLessThan]]) -> int:
    if key is None:
        okey = seq.__getitem__
    else:
        def okey(i):
            return key(seq[i])

    return max(range(len(seq)), key=okey)


def index_of_or_none(seq: Sequence[_T], value: Any) -> Optional[int]:
    """
    :param seq: the sequence to search in
    :param value: the value to search for
    :return: the index of `value` in `seq` or `None` if `value not in seq`
    """
    try:
        return seq.index(value)
    except ValueError:
        return None


def single_or_raise(seq: Sequence[_T]) -> _T:
    """
    :param seq: the seq to access
    :return: the first element of this sequence if `len(seq) == 1`  otherwise raise `ValueError`
    """
    if (l := len(seq)) != 1:
        raise ValueError(f"expecting single element, found: {l}")
    return seq[0]


def get_or_default(seq: Sequence[_T], index: int, default: _T) -> _T:
    """
    :param seq: the sequence to access
    :param index: the index to get
    :param default: the value to return if `-len(seq) > index > len(seq)`
    :return: the value of `seq[index]` if such exists (no IndexError had been thrown upon accessing index),
             otherwise returns the `default` value
    """
    if -len(seq) > index > len(seq):
        return default
    return seq[index]


def strs(seq: Sequence[_T]) -> List[str]:
    """
    :param seq: the sequence to extract items from
    :return: list containing `str(item)` for each item in `seq`
    """
    return [str(it) for it in seq]


def pop_or_none(stack: StackLike[_T]) -> Optional[_T]:
    """
    pops an item from the given stack-like object, if it empty, return None
    :param stack: the stack to pop an item from
    :return: poped item or None
    """

    if len(stack) > 0:
        return stack.pop()
    return None
