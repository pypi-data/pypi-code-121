import functools
import gc
import hashlib
import operator
import os
import sys
from functools import reduce  # forward compatibility for Python 3
from typing import Iterable
import numpy as np


def get_from_dict(data_dict, map_list: Iterable):
    return reduce(operator.getitem, map_list, data_dict)


def set_in_dict(data_dict, map_list, value):
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


sentinel = object()


def rgetattr(obj, attr, default=sentinel):
    if default is sentinel:
        _getattr = getattr
    else:

        def _getattr(obj, name):
            return getattr(obj, name, default)

    return functools.reduce(_getattr, [obj] + attr.split("."))


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def get_next_file_index(directory, pattern):
    highest = -1
    for fname in os.listdir(directory):
        find = pattern.search(fname)
        if find is not None:
            if int(find.group(1)) > highest:
                highest = int(find.group(1))
    highest += 1
    return highest


def fullname(o):
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + "." + o.__class__.__name__


def get_object_refs(o):
    ref_count = sys.getrefcount(o)
    if ref_count > 0:
        print("Number of referrers of object {} is {}".format(o, ref_count))
        for index, referrer in enumerate(gc.get_referrers(o)):
            print(index, referrer)


def is_equal(a, b):
    c = a == b
    if isinstance(c, np.ndarray):
        c = c.all()
    return c


def compute_MD5(my_string):
    m = hashlib.md5()
    m.update(my_string.encode("utf-8"))
    return m.hexdigest()
