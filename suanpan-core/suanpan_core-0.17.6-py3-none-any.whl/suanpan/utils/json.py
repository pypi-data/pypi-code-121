# coding=utf-8
from __future__ import absolute_import, print_function
import sys
import datetime
import functools
import json
from suanpan import path
from suanpan.lazy_import import lazy_import

if sys.platform == "win32":
    import numpy as np
    import pandas as pd
else:
    np = lazy_import('numpy')
    pd = lazy_import('pandas')


class SPEncoder(json.JSONEncoder):
    INNER_DATETIME = (datetime.datetime,)

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, self.INNER_DATETIME):
            return obj.replace(tzinfo=datetime.timezone.utc).isoformat()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


if sys.version_info.minor < 9:
    _load = functools.partial(json.load, encoding="utf-8")
    _loads = functools.partial(json.loads, encoding="utf-8")
else:
    _load = functools.partial(json.load)
    _loads = functools.partial(json.loads)
_dump = functools.partial(json.dump, ensure_ascii=False, cls=SPEncoder)
_dumps = functools.partial(json.dumps, ensure_ascii=False, cls=SPEncoder)


def _loadf(file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(file, "r", encoding=encoding) as _file:
        return _load(_file, *args, **kwargs)


def _dumpf(s, file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    path.safeMkdirsForFile(file)
    with open(file, "w", encoding=encoding) as _file:
        return _dump(s, _file, *args, **kwargs)


def load(file, *args, **kwargs):
    _l = _loadf if isinstance(file, str) else _load
    return _l(file, *args, **kwargs)


def dump(s, file, *args, **kwargs):
    _d = _dumpf if isinstance(file, str) else _dump
    return _d(s, file, *args, **kwargs)


loads = _loads
dumps = _dumps
