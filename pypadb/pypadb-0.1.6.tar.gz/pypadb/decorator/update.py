import functools

from ..utils.query_util import parse_sql_where, parse_sql_update, execute


def update(sql: str):
    def deco(fun):
        @functools.wraps(fun)
        def wrapper(data, **kwargs):
            fun(data)
            in_sql, query_dict = parse_sql_update(sql, data)
            in_sql = parse_sql_where(in_sql, kwargs)
            execute(in_sql, {**query_dict, **kwargs})

        return wrapper

    return deco
