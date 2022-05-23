from collections.abc import Iterable
from itertools import chain


def listify(var):
    if var is None:
        return ()
    elif isinstance(var, str):
        return tuple(var.split(","))
    elif isinstance(var, Iterable):
        return tuple(var)
    else:
        raise TypeError


def peek(it, default=None):
    try:
        el = pop(it)
        return el, chain([el], it)
    except StopIteration:
        # Empty sequence
        return default, it

def pop(it):
    return next(it)
