import functools
from sqlalchemy.schema import CreateTable
from .models import *


def parse_key(expr_key, model_cls):
    if '.' in expr_key:
        full_path = expr_key.split('.')
        field = full_path[0]
        path = '.'.join(['$', *full_path[1:]])
        return sa.func.json_value(getattr(model_cls, field), path)
    else:
        return getattr(model_cls, expr_key)


def parse_expr(expr_key, expr_value, model_cls):
    if expr_key == '$or':
        return sa.or_(*[parse_expr(k, v, model_cls)\
                        for i in expr_value for k, v in i.items()])
    elif expr_key == '$in':
        return parse_key(expr_value[0], model_cls).in_(expr_value[1])
    elif expr_key == '$ne':
        return parse_key(expr_value[0], model_cls) != (expr_value[1])
    elif expr_key == '$lt':
        return parse_key(expr_value[0], model_cls) < (expr_value[1])
    elif expr_key == '$gt':
        return parse_key(expr_value[0], model_cls) > (expr_value[1])
    else:
        return parse_key(expr_key, model_cls) == expr_value


def create_table():
    ret = []
    for k, v in globals().items():
        if hasattr(v, '__table__'):
            ret.append(str(CreateTable(v.__table__).compile(engine)).strip() + ';')
    return '\n\n'.join(ret)


def get_list_query(model_cls, order_by=None, **kwargs):
    q = session.query(model_cls)
    for k, v in kwargs.items():
        q = q.filter(parse_expr(k, v, model_cls))
    if order_by:
        if isinstance(order_by, str) and order_by.startswith('-'):
            q = q.order_by(parse_key(order_by[1:], model_cls))
        elif isinstance(order_by, str):
            q = q.order_by(parse_key(order_by, model_cls))
    return q


def get_inst(model_cls, **kwargs):
    inst = get_list_query(model_cls, **kwargs).first()
    return inst
