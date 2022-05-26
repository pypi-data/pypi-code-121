from itertools import chain, islice, tee


def flatten(list_of_lists):
    """
    Flatten one level of nesting.

    From https://docs.python.org/3.7/library/itertools.html#itertools-recipes.
    """
    return chain.from_iterable(list_of_lists)


def pairwise(iterable):
    """
    s -> (s0,s1), (s1,s2), (s2, s3)

    From https://docs.python.org/3.7/library/itertools.html#itertools-recipes.
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def take(n, iterable):
    """
    Return first n items of the iterable as a list.

    From https://docs.python.org/3/library/itertools.html#itertools-recipes.
    """
    return list(islice(iterable, n))
