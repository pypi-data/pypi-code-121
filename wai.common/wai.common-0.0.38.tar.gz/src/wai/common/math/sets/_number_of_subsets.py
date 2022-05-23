from .._factorial import factorial


def number_of_subsets(
        set_size: int,
        subset_size: int,
        order_matters: bool = False,
        can_reselect: bool = False
):
    """
    Gets the number of ways to choose ``subset_size`` items from a set of
    ``set_size`` possibilities.

    :param set_size:
                The number of items to select from.
    :param subset_size:
                The number of items to select.
    :param order_matters:
                Whether selections of the same items but in a different selection-order
                are considered distinct subsets.
    :param can_reselect:
                Whether the same item can appear more than once in a subset.
    :return:
                The number of possible subsets that could be selected.
    """
    # Sets can't have negative size
    if set_size < 0:
        raise ArithmeticError(f"Can't have a set of {set_size} items")
    if subset_size < 0:
        raise ArithmeticError(f"Can't have a subset of {subset_size} items")

    # Can only ever select 1 subset of size zero, the empty set
    if subset_size == 0:
        return 1

    # If there are no items to select from, the empty set is the only possible selection,
    # so any subsets of greater size are impossible
    if set_size == 0:
        return 0

    # Handle reselection separately
    if can_reselect:
        # If order matters, (n, k) = n^k
        if order_matters:
            return set_size ** subset_size

        # Otherwise, (n, k) = (n + k - 1, k) (without reselection). Rather than recursing, we
        # just fall through with a modified n
        set_size += subset_size - 1

    else:
        # Without reselection, we can't select more items than are in the set
        if subset_size > set_size:
            return 0

    # If order matters, (n, k) = n! / (n - k)! (without reselection)
    if order_matters:
        return factorial(set_size, set_size - subset_size)

    # Otherwise, (n, k) = n! / k!(n - k)! (again, without reselection).
    # We discriminate on the difference between n and k to determine
    # the least number of multiplications to perform
    remainder_size = set_size - subset_size
    if subset_size > remainder_size:
        return factorial(set_size, subset_size) // factorial(remainder_size)
    else:
        return factorial(set_size, remainder_size) // factorial(subset_size)
