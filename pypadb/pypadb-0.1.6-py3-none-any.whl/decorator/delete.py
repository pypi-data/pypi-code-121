import functools

from ..utils import inspect_util
from ..utils.query_util import execute


def delete(sql: str):
    def deco(fun):
        @functools.wraps(fun)
        def wrapper(*args):
            fun(*args)
            execute(sql, dict(zip([a.name for a in inspect_util.arg_list(fun)], args)))

        return wrapper

    return deco
