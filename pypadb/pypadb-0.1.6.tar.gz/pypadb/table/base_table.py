from typing import Any, Union

from ..utils.conditions import Limit, Like
from ..utils.enums import QueryModeEnum
from ..utils.query_util import query, execute, parse_sql_batch, parse_sql_where, parse_sql_update


class BaseTable:
    __slots__ = ['name', 'data_type', 'base_select_sql']

    name: str
    data_type: Any
    base_select_sql: str

    def __init__(self, name: str, data_type):
        self.name = name
        self.data_type = data_type
        self.base_select_sql = f'select * from {name}'

    def select_one(self, extra=None, **kwargs):
        res, _ = query(parse_sql_where(self.base_select_sql, kwargs), kwargs, self.data_type, QueryModeEnum.One)
        return extra(res) if extra else res

    def select_many(self, limit: Limit = None, extra=None, **kwargs) -> list:
        res, _ = query(parse_sql_where(self.base_select_sql, kwargs, limit), kwargs, self.data_type, QueryModeEnum.Many)
        return extra(res) if extra else res

    def select_like(self,
                    likes: Union[list[Like], Like] = {},
                    limit: Limit = None,
                    extra=None) -> list:
        sql: str = self.base_select_sql
        data_dict: dict = {}
        if likes:
            sql += ' where'
            if isinstance(likes, list):
                for like in likes:
                    sql += f'{like} and'
                    data_dict[like.column] = like.value
                sql = sql.rstrip(' and')
            else:
                sql += str(likes)
                data_dict[likes.column] = likes.value
        res, _ = query(sql + str(limit) if limit else sql, data_dict, self.data_type, QueryModeEnum.Many)
        return extra(res) if extra else res

    def update(self, entity, **kwargs):
        if not kwargs:
            return
        sql = f'update {self.name}'
        sql, query_dict = parse_sql_update(sql, entity)
        sql = parse_sql_where(sql, kwargs)
        _, row_id = execute(sql, {**query_dict, **kwargs})
        return row_id

    def delete(self, **kwargs):
        if not kwargs:
            return
        sql = f'delete from {self.name}'
        sql = parse_sql_where(sql, kwargs)
        return execute(sql, kwargs)

    def insert(self, data) -> int:
        sql = f'insert into {self.name}('
        tmp = '('
        data_dict: dict = data.dict()
        for key in data_dict:
            if data_dict[key] or data_dict[key] == 0:
                sql += f'{key}, '
                tmp += f'%({key})s, '
        tmp = tmp.rstrip(', ') + ')'
        sql = sql.rstrip(', ') + ') value' + tmp
        _, row_id = execute(sql, data_dict)
        return row_id

    def insert_batch(self, data: list) -> int:
        sql = f'insert into {self.name}('
        data_dict: dict = data[0].dict()
        columns: list = []
        for key in data_dict:
            if data_dict[key] or data_dict[key] == 0:
                sql += f' {key}, '
                columns.append(key)
        sql = sql.rstrip(', ') + ') values '

        parse_res, query_dict = parse_sql_batch(columns, data)

        _, row_id = execute(sql + parse_res, query_dict)
        return row_id
