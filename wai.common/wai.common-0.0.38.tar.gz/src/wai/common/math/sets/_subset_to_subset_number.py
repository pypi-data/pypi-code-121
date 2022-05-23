from typing import List

from ._number_of_subsets import number_of_subsets


def subset_to_subset_number(
        set_size: int,
        subset: List[int],
        order_matters: bool = False,
        can_reselect: bool = False
) -> int:
    """
    Encodes a subset of the integers in [0, ``set_size``) as a single integer.

    :param set_size:
                The number of items to select from.
    :param subset:
                The selected items by index.
    :param order_matters:
                Whether the selection order of the subset should be encoded as well.
    :param can_reselect:
                Whether duplicate items are allowed in the subset.
    :return:
                A numeric encoding of the subset.
    """
    # Cache the size of the subset
    subset_size = len(subset)

    # Sets can't have negative size
    if set_size < 0:
        raise ArithmeticError(f"'set_size' must be non-negative, got {set_size}")

    # The empty set is the only possible subset of size 0, so encode it as the smallest representation
    if subset_size == 0:
        return 0

    # If there are no items to select from, the empty set is the only possible selection,
    # so any subsets of greater size are impossible
    if set_size == 0:
        raise ArithmeticError(
            f"Can't select a non-empty subset (subset size = {subset_size}) from the empty set"
        )

    # Make sure all values are in [0, n)
    if not all(0 <= x < set_size for x in subset):
        raise ArithmeticError(
            f"Subset contains values outside the valid range for a set-size of {set_size}: {subset}"
        )

    # Handle reselection separately
    if can_reselect:
        # If order matters, shift-encode each value in order
        if order_matters:
            return sum(
                value * (set_size ** index)
                for index, value in enumerate(subset)
            )

        # Otherwise, convert to the equivalent binomial representation and fall-through encode
        counts = {}
        for value in subset:
            counts[value] = counts[value] + 1 if value in counts else 1
        subset = []
        for i in range(set_size - 1):
            last = -1 if len(subset) == 0 else subset[-1]
            subset.append(last + 1 + (0 if i not in counts else counts[i]))
        set_size += subset_size - 1
        subset_size = set_size - subset_size

    else:
        # If not allowed to reselect, subset cannot contain duplicates
        seen = set()
        for value in subset:
            if value in seen:
                raise ArithmeticError(f"Duplicate items in subset: {subset}")
            seen.add(value)

    # If the order matters, shift-encode the items, reducing the problem to (n - 1, k -1)
    # at each iteration
    if order_matters:
        result = subset[0]
        subset = [x - 1 if x > result else x for x in subset[1:]]
        factor = set_size - 1
        while len(subset) > 0:
            result *= factor
            next = subset[0]
            result += next
            factor -= 1
            subset = [x - 1 if x > next else x for x in subset[1:]]

        return result

    # If order doesn't matter, encode the subset as an arithmetic encoding
    sorted = list(subset) if not can_reselect else subset
    sorted.sort(reverse=True)
    return sum(number_of_subsets(n, subset_size - k) for k, n in enumerate(sorted))
