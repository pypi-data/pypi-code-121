from collections.abc import Iterable
from re import split
from typing import Union
from numbers import Number

def is_non_string_iterable(value):
    return isinstance(value, Iterable) and not isinstance(value, str)

def to_sql_range(values:Union[Number, Iterable], column: str, table:str = '', op='IN'):
    if not isinstance(values, Iterable):
        values = [values]
    
    __left_bracket, __join_by, __right_bracket = ('"', '|', '"') if op.lower() == 'regexp' else ('(', ', ', ')')

    __values = __join_by.join([str(value) for value in values])

    _column = f'{table}.{column}' if table else column

    return f'{_column} {op} {__left_bracket}{__values}{__right_bracket}'
