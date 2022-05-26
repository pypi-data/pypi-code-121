from math import isclose

from . import flatten, take


def compact(list_of_lists):
    """
    Compacts a list of lists.

    This is the same as flattening but also returns the compactification scheme, i.e. a list of lengths of the original
    sub-lists that were flattened. This is intended to be used with `uncompact`.
    """
    compacted = list(flatten(list_of_lists))
    compactification = list(map(len, list_of_lists))

    return compacted, compactification


def uncompact(compacted, compactification):
    """
    Reverses the compactification from `compact`.
    """
    fli = iter(compacted)
    return list(list(take(c, fli)) for c in compactification)


def intersperse(lists, elem):
    """
    Returns `lists[0], elem, lists[1], elem, lists[2], ..., elem, list[-1]`.
    """
    if len(lists) == 0:
        return

    listiter = iter(lists)
    yield from next(listiter)
    for l in lists:
        yield elem
        yield from l


def deresolve(x):
    """
    Removes redundant points that are too close to each other using `math.isclose`.

    :param x:
        Iterable to remove close points of.
    :return:
        A list of points with redundant close points removed.
    """

    xiter = iter(x)
    try:
        result = [next(xiter)]
    except StopIteration:
        return []

    for p in xiter:
        if not isclose(result[-1], p):
            result.append(p)

    return result
