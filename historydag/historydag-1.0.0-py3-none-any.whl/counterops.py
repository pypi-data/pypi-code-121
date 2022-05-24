"""Functions for manipulating :class:`collections.Counter` objects."""

from collections import Counter
import historydag.utils as utils


def counter_prod(counterlist, accumfunc):
    """'multiply' two Counters. Really a sort of cartesian product, which does
    accumfunc to keys and counts all the ways each result can be achieved using
    contents of counters in counterlist.

    accumfunc must be a function like sum which acts on a list of
    arbitrary length. Probably should return an object of the same type.
    """
    newc = Counter()
    for combi in utils.cartesian_product([c.items for c in counterlist]):
        weights, counts = [[t[i] for t in combi] for i in range(len(combi[0]))]
        newc.update({accumfunc(weights): utils.prod(counts)})
    return newc


def counter_sum(counterlist, counter_type=Counter):
    """Sum a list of counters.

    Equivalent to concatenating their representative lists.
    """
    newc = counter_type()
    for c in counterlist:
        newc += c
    return newc
