from typing import Iterable, Union, Sequence, TypeVar

SequenceType = TypeVar("SequenceType", bound=Sequence)


def flatten(sequence: SequenceType, depth: int = -1) -> SequenceType:
    """
    Flattens a sequence into a new sequence of the same type.
    Expects that the sequence-type's __init__ method takes an
    iterator (as in list and tuple).

    :param sequence:    The sequence to flatten.
    :param depth:       The number of nested levels to flatten. Set to a negative number
                        to flatten all levels.
    :return:            A new sequence of the same type, but flattened.
    """
    # Use flattening iterator to initialise a new sequence of the same type
    from ..iterate import flatten
    return type(sequence)(flatten(sequence, depth))


def normalise_index(index: int, length: Union[int, Sequence]) -> int:
    """
    Normalises the given list index into the valid range for a
    list of the given length. This way negative indices index
    backward from the end of the list.

    :param index:   The index to normalise.
    :param length:  The sequence length to normalise to, or a sequence.
    :return:        The normalised index.
    """
    # Get the length if we're given a sequence
    if not isinstance(length, int):
        length = len(length)

    return index % length


def extract_by_index(sequence: SequenceType, indices: Iterable[int]) -> SequenceType:
    """
    Extracts elements of the given sequence. Returned type is the
    same as the given sequence. Expects that the sequence-type's
    __init__ method takes an iterator (as in list and tuple).

    :param sequence:    The sequence to get elements from.
    :param indices:     The indices of the elements to get.
    :return:            The selected elements.
    """
    # Use extracting iterator to initialise a new sequence of the same type
    from ..iterate import extract_by_index
    return type(sequence)(extract_by_index(sequence, indices))


def binary_search(sequence: Sequence[int], target: int) -> int:
    """
    Performs as binary search on an ordered sequence of ints to
    find the index of the first value greater than or equal to
    the target value.

    :param sequence:    The order sequence of ints.
    :param target:      The target value to find.
    :return:            The index of the found element.
    """
    start = 0
    end = len(sequence)
    while end != start:
        pivot = (start + end) // 2
        if sequence[pivot] >= target:
            end = pivot
        else:
            start = pivot + 1

    return start
