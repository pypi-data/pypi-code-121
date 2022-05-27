#!/usr/bin/env python3

import parametrize_from_file as pff

with_repr = pff.Namespace('import reprfunc', 'from reprfunc import *')

def get_obj(d):
    try:
        return d['obj']
    except KEyError:
        return d['Obj']()


@pff.parametrize
def test_repr(obj, expected):
    obj = with_repr.exec(obj, get=get_obj)
    assert repr(obj) == expected

@pff.parametrize
def test_repr_builder(builder, expected):
    class Obj:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    builder = with_repr.fork(Obj=Obj).exec(builder, get='builder')
    assert str(builder) == expected

