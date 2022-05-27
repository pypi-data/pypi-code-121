from types import FunctionType, LambdaType, MethodType
from typing import Iterable
import re


lambda_in_oper = {
    'in': 'in',
    'notin': 'notin'
}

lambda_map_oper = {
    'map': 'map'
}

lambda_regex_oper = {
    're': 're'
}

lambda_query_oper = {
    'gt': '>',
    'eq': '==',
    'ne': '!=',
    'lt': '<',
    'ge': '>=',
    'le': '<=',
    None: '==',
    **lambda_regex_oper
}

lambda_oper = {
    **lambda_query_oper,
    **lambda_in_oper,
    **lambda_map_oper
}

lambda_when = {
    'before': 'before',
    'after': 'after'
}

lambda_handle = {
    'lower': lambda x: str(x).lower(),
    'upper': lambda x: str(x).upper(),
}
lambda_handle['lower'].__name__ = 'lower'
lambda_handle['upper'].__name__ = 'upper'


class Operator(object):

    def __init__(self, field_name, oper, value, when=None, handle=None):
        self.field_name = field_name
        self.oper = oper
        self.value = value
        self.when = when
        self.handle = handle

    def __call__(self, df):
        df = self.when_handle(df, 'before')
        return self.when_handle(self.do_oper(df), 'after')

    def do_oper(self, df):
        raise NotImplementedError

    def when_handle(self, df, when):
        if self.when and self.when == when:
            df[self.field_name] = df[self.field_name].map(self.handle)
        return df

    def __str__(self):

        return '<%s field=> %s, oper=> %s, value=> %s, when=%s, handle=%s>' % (
            self.__class__.__name__,
            self.field_name,
            self.oper,
            self.value,
            self.when,
            self.handle and self.handle.__name__
        )


class EmptyOper(Operator):

    def __init__(self, field_name, oper, value, when=None, handle=None):
        pass

    def __call__(self, df):
        return df

    def do_oper(self, df):
        return df


class MapOper(Operator):

    def __init__(self, field_name, oper, value, when=None, handle=None):
        assert isinstance(value, (
            FunctionType,
            LambdaType,
            MethodType,
            dict
        )), TypeError()
        super().__init__(field_name, oper, value, when, handle)
        self.field_name = field_name
        self.oper = oper
        self.value = value

    def do_oper(self, df):
        df[self.field_name] = df[self.field_name].map(self.value)
        return df


class InOper(Operator):

    def __init__(self, field_name, oper, value, when=None, handle=None):
        assert type(value) != str and isinstance(value, Iterable), TypeError()
        super().__init__(field_name, oper, value, when, handle)
        self.field_name = field_name
        self.oper = oper
        self.value = value

    def do_oper(self, df):
        query = df[self.field_name].isin(self.value)
        if self.oper == 'notin':
            return df[~query].reset_index(drop=True).copy()
        return df[query].reset_index(drop=True).copy()


class QueryOper(Operator):

    def __init__(self, field_name, oper, value, when=None, handle=None):
        assert isinstance(value, (str, int, float)), TypeError()
        super().__init__(field_name, oper, value, when, handle)
        self.field_name = field_name
        self.oper = lambda_query_oper[oper]
        self.value = value

    def do_oper(self, df):
        if self.oper == 're':
            return df[
                df[self.field_name].map(
                    lambda x:bool(re.search(self.value, x, re.I | re.S))
                )
            ].reset_index(drop=True).copy()

        if type(self.value) is str:
            self.value = '"' + self.value.strip('"').strip("'") + '"'
        else:
            self.value = str(self.value)
        query_lambda = '%s %s %s' % (
            self.field_name,
            self.oper,
            self.value
        )
        return df.query(query_lambda).reset_index(drop=True).copy()


def make_query(field_name, oper, value, when=None, handle=None):
    if oper in lambda_in_oper:
        return InOper(field_name, oper, value, when, handle)
    if oper in lambda_map_oper:
        return MapOper(field_name, oper, value, when, handle)
    if oper in lambda_query_oper:
        return QueryOper(field_name, oper, value, when, handle)
    return EmptyOper(field_name, oper, value, when, handle)
