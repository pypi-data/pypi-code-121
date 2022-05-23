from typing import List

from ._number_of_subsets import number_of_subsets


def subset_number_to_subset(
        set_size: int,
        subset_size: int,
        subset_number: int,
        order_matters: bool = False,
        can_reselect: bool = False
) -> List[int]:
    """
    Decodes the result of ``subset_to_subset_number`` into the original subset.

    :param set_size:
                The number of items that were selected from.
    :param subset_size:
                The number of items that were selected.
    :param subset_number:
                The encoded number of the subset, in [0, (n, k)).
    :param order_matters:
                Whether the selection order of the subset was encoded as well.
    :param can_reselect:
                Whether duplicate items were allowed in the subset.
    :return:
                The originally-encoded subset.
    """
    # Sets can't have negative size
    if set_size < 0:
        raise ArithmeticError(f"Can't have a set of {set_size} items")
    if subset_size < 0:
        raise ArithmeticError(f"Can't have a subset of {subset_size} items")

    # Start with the empty set
    subset = []

    # The empty set is the only possible subset of size 0, so return it
    if subset_size == 0:
        # Subset number should be 0 for a subset size of 0
        if subset_number != 0:
            raise ArithmeticError(
                f"0 is the only valid subset number for subsets of size 0, got {subset_number}"
            )

        return subset

    # If there are no items to select from, the empty set is the only possible selection,
    # so any subsets of greater size are impossible
    if set_size == 0:
        raise ArithmeticError(
            f"Can't select a non-empty subset (subset size = {subset_size}) from the empty set"
        )

    # Special case for order-dependent
    if order_matters:
        # Ordered with reselection is shift-encoded, so simply shift-decode
        if can_reselect:
            while len(subset) < subset_size:
                subset.append(subset_number % set_size)
                subset_number //= set_size

        # Without reselection, the items available for selection reduces by 1 at each iteration
        else:
            factor = set_size - subset_size + 1
            while len(subset) < subset_size:
                next = subset_number % factor
                subset_number //= factor
                for index in range(len(subset)):
                    if subset[index] >= next:
                        subset[index] += 1
                subset.insert(0, next)
                factor += 1

        return subset

    # If reselect is allowed, we are expecting the equivalent binomial representation of the selection
    if can_reselect:
        set_size += subset_size - 1
        subset_size = set_size - subset_size

    # Decode the arithmetic encoding of the binomial representation
    num_subsets = number_of_subsets(set_size - 1, subset_size)
    k = subset_size
    for n in reversed(range(set_size)):
        if subset_number >= num_subsets:
            subset_number -= num_subsets
            subset.append(n)
            if len(subset) == subset_size:
                break
            num_subsets = num_subsets * k // n
            k -= 1
        elif n != 0:
            num_subsets = num_subsets * (n - k) // n

    # Convert the binomial representation back to the original multinomial one if reselection was enabled
    if can_reselect:
        subset.sort()
        subset_size = set_size - subset_size
        set_size -= subset_size - 1
        counts = {}
        total = 0
        for i in range(set_size - 1):
            last = -1 if i == 0 else subset[i - 1]
            count = subset[i] - last - 1
            total += count
            if count != 0:
                counts[i] = count
        if total < subset_size:
            counts[set_size - 1] = subset_size - total
        subset = []
        for value, count in counts.items():
            for i in range(count):
                subset.append(value)

    return subset
