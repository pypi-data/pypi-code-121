import os
from collections.abc import Mapping, Sequence
import numbers


def is_number(n):
    return isinstance(n, numbers.Number)


def is_mapping(d):
    return isinstance(d, Mapping)


def is_dict(d):
    return isinstance(d, dict)


def is_bool(d):
    return isinstance(d, bool)


def is_class(c):
    return isinstance(c, type)


def is_sequence(l):
    return isinstance(l, Sequence)


def is_non_empty_string(s):
    return isinstance(s, str) and len(s) > 0


def is_file(fname):
    return os.path.isfile(fname)


def is_callable(func):
    return callable(func)


def is_int_sequence(seq):
    if not is_sequence(seq):
        return False

    for v in seq:
        if not is_number(v):
            return False

    return True


def sequences_are_compatible(seq0, seq1):
    return len(seq0) == len(seq1)
