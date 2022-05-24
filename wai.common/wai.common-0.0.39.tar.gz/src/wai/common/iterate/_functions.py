from random import Random, shuffle
from typing import Iterable, Iterator, Optional, Sequence, Tuple, List, Any

from .._typing import Predicate, T


def is_iterable(obj) -> bool:
    """
    Determines if the given object is an iterable.

    :param obj:     The object to check.
    :return:        True if the object is iterable,
                    False if not.
    """
    return safe_iter(obj) is not None


def safe_iter(obj) -> Optional[Iterator]:
    """
    Returns an iterator for the object if it's iterable,
    or None if it's not.

    :param obj:     The object to get the iterator for.
    :return:        The iterator, or None if it's not iterable.
    """
    try:
        return iter(obj)
    except Exception:
        return None


def flatten(iterable: Iterable, depth: int = -1) -> Iterator:
    """
    Gets an iterator for the given iterable, which will
    flatten any iterable elements into the iterator output.

    :param iterable:    The iterable.
    :param depth:       The number of nested levels to flatten. Set to a negative number
                        to flatten all levels.
    :return:            A flattening iterator over the iterable.
    """
    # Process each element of the iterable in turn
    for element in iterable:
        # Try to get an iterator for the element
        element_iter = safe_iter(element)

        # If the element isn't iterable or we've reached depth, yield the element itself
        if element_iter is None or depth == 0:
            yield element

        # Otherwise yield each sub-element of the flattened element
        else:
            for sub_element in flatten(element_iter, depth - 1):
                yield sub_element


def invert_indices(indices: Iterable[int], size: int) -> Iterator[int]:
    """
    Returns the indices that are not in the given indices, up to the given size.

    :param indices:     The indices to invert.
    :param size:        The exclusive maximum index.
    :return:            A inverted indices.
    """
    index_set = set(indices)

    for i in range(size):
        if i not in index_set:
            yield i


def extract_by_index(sequence: Sequence, indices: Iterable[int]) -> Iterator:
    """
    Extracts elements of the given sequence.

    :param sequence:    The sequence to get elements from.
    :param indices:     The indices of the elements to get.
    :return:            The selected elements.
    """
    for index in indices:
        yield sequence[index]


def first(iterable: Iterable[T], predicate: Predicate[T]) -> Tuple[int, Optional[T]]:
    """
    Finds the first value in an iterable to meet a given predicate.

    :param iterable:    The iterable to search.
    :param predicate:   The predicate to match.
    :return:            The enumerated position of and element found.
    """
    for iteration, value in enumerate(iterable):
        if predicate(value):
            return iteration, value

    # Predicate not satisfied
    return -1, None


def random(iterator: Iterator[T], rand: Random = None) -> Iterator[T]:
    """
    Returns the elements of the given iterator in a random order, as
    determined by the given source of randomness.

    :param iterator:    The iterator to randomise.
    :param rand:      The source of randomness.
    :return:            An iterator over the same elements in random order.
    """
    # Buffer the elements of the iterator
    buffer: List[T] = list(iterator)

    # Shuffle them
    if rand is not None:
        rand.shuffle(buffer)
    else:
        shuffle(buffer)

    return iter(buffer)


def all_meet_predicate(iterable: Iterable[T], predicate: Predicate[T]) -> bool:
    """
    Version of all which checks values against a predicate.

    :param iterable:    An iterable of values.
    :param predicate:   A predicate which checks those values.
    :return:            True if all values meet the predicate,
                        False if not.
    """
    return all(map(predicate, iterable))


def any_meets_predicate(iterable: Iterable[T], predicate: Predicate[T]) -> bool:
    """
    Version of any which checks values against a predicate.

    :param iterable:    An iterable of values.
    :param predicate:   A predicate which checks those values.
    :return:            True if any value meets the predicate,
                        False if not.
    """
    return any(map(predicate, iterable))


def count(iterable: Iterable[Any]) -> int:
    """
    Returns the number of items in the iterable by counting them.

    :param iterable:    The iterable.
    :return:            The number of items in the iterable.
    """
    return sum(1 for _ in iterable)
