import functools
import re
from typing import Callable

from ..utils.query_util import execute, parse_sql_batch


def insert(sql: str) -> Callable:
    arg_list = [s.strip() for s in re.findall(r'[(](.*?)[)]', sql)[0].split(',')]
    sql += ' values'

    def deco(fun):
        @functools.wraps(fun)
        def wrapper(data):
            in_sql = sql
            if not isinstance(data, list):
                fun(data)
                template_sql = '('
                for arg in arg_list:
                    template_sql += f'%({arg})s,'
                template_sql = template_sql.rstrip(',') + '),'
                _, row_id = execute(in_sql + template_sql, data.dict())
                return row_id

            for i in data:
                fun(i)
            parse_res, query_dict = parse_sql_batch(arg_list, data)

            _, row_id = execute(in_sql + parse_res, query_dict)
            return row_id

        return wrapper

    return deco
