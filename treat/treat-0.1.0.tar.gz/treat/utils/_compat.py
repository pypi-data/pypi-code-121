import sys

from collections import OrderedDict


PY38 = sys.version_info >= (3, 8)


if PY38:
    ReversableDict = dict
else:
    ReversableDict = OrderedDict
