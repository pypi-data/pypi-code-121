from ._number_of_subsets import number_of_subsets


def number_of_permutations(size: int) -> int:
    """
    Calculates the number of possible permutations of a collection
    of the given size.

    :param size:
                The number of items in the collection.
    :return:
                The number of possible permutations of a collection
                of the given size.
    """
    return number_of_subsets(size, size, True)
