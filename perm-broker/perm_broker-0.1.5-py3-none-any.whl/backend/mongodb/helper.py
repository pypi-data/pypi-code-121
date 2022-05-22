import functools
import mongoengine as mg
from . import models


def parse_key(expr_key):
    return expr_key.replace('.', '__')


def parse_expr(expr_key, expr_value):
    if expr_key == '$or':
        parsed_value = [parse_expr(k, v) for i in expr_value for k, v in i.items()]
        return functools.reduce(lambda x, y: x | y,
                                parsed_value)
    elif expr_key == '$in':
        return mg.Q(**{('%s__in' % parse_key(expr_value[0])): expr_value[1]})
    elif expr_key in ('$ne', '$lt', '$gt'):
        return mg.Q(**{('%s__%s' % (parse_key(expr_value[0])), expr_key): expr_value[1]})
    else:
        return mg.Q(**{parse_key(expr_key): expr_value})


def get_list_query(model_cls, order_by=None, **kwargs):
    q = model_cls.objects
    for k, v in kwargs.items():
        q = q.filter(parse_expr(k, v))
    if order_by:
        q = q.order_by(order_by)
    return q


def get_inst(model_cls, **kwargs):
    inst = get_list_query(model_cls, **kwargs).first()
    return inst
