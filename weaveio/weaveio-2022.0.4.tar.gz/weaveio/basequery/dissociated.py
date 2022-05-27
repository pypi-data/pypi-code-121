from functools import partial
from typing import Union, Callable

import numpy as np
import py2neo
from astropy.table import Table

from .common import FrozenQuery, is_regex
from .tree import Branch
from ..hierarchy import Hierarchy
from ..writequery import CypherVariable, CypherQuery

__all__ = ['sum', 'min', 'max', 'std', 'all', 'any', 'count', 'abs', 'floor', 'ceil', 'round',
           'random', 'sign', 'log', 'log10', 'exp', 'sqrt', 'string', 'lower', 'upper']


def _template_aggregator(string_function, name, normal: Callable, item: 'Dissociated', wrt: FrozenQuery = None,
                         remove_infs: bool = True, convert_to_float: bool = False, allow_hiers=False,
                         args=None, kwargs=None):
    if not isinstance(item, FrozenQuery):
        if wrt is not None:
            args = (wrt, ) + args
        return normal(item, *args, **kwargs)
    elif wrt is None:
        branch = item.branch.handler.entry
    else:
        branch = wrt.branch
    if isinstance(item, Dissociated):
        itembranch, itemvariable = _convert(item.branch, item.variable, remove_infs, convert_to_float)
        new = branch.aggregate(string_function, itemvariable, itembranch, namehint=name)
    elif allow_hiers:
        new = branch.aggregate(string_function, item.hierarchy_variable, item.branch, namehint=name)
    else:
        raise TypeError(f"Calling {name} with {item} of type {type(item)} is not supported")
    return Dissociated(item.handler, new, new.action.target)


def _convert(branch: Branch, variable: CypherVariable, remove_infs: bool = True, convert_to_float: bool = False):
    if convert_to_float:
        branch = branch.operate('CASE WHEN {z} = true THEN 1 WHEN {z} = false THEN 0 ELSE {z} END', namehint='convert_to_float', z=variable)
        variable = branch.action.output_variables[0]
    if remove_infs:
        branch = branch.operate("CASE WHEN {variable} > apoc.math.maxLong() THEN null ELSE {variable} END", namehint='remove_infs', variable=variable)
        variable = branch.action.output_variables[0]
    return branch, variable


def _template_operator(string_function, name, normal: Callable, item: 'Dissociated', remove_infs: bool = True, convert_to_float: bool = False, args=None, kwargs=None):
    if not isinstance(item, FrozenQuery):
        return normal(item, *args, **kwargs)
    branch, variable = _convert(item.branch, item.variable, remove_infs, convert_to_float)
    branch = branch.operate(string_function, x=variable, namehint=name)
    return Dissociated(item.handler, branch, branch.action.output_variables[0])


python_abs = abs
python_round = round


def abs(item, *args, **kwargs):
    return _template_operator('abs({x})', 'abs', python_abs, item, convert_to_float=True, args=args, kwargs=kwargs)


def ceil(item, *args, **kwargs):
    return _template_operator('ceil({x})', 'ceil', np.ceil, item, convert_to_float=True, args=args, kwargs=kwargs)


def floor(item, *args, **kwargs):
    return _template_operator('floor({x})', 'floor', np.floor, item, convert_to_float=True, args=args, kwargs=kwargs)


def random(item, *args, **kwargs):
    return _template_operator('random({x})', 'random', np.uniform, item, convert_to_float=True, args=args, kwargs=kwargs)


def round(item, precision=0, *args, **kwargs):
    return _template_operator('round({x})', 'round', partial(python_round, precision), item, convert_to_float=True, args=args, kwargs=kwargs)


def sign(item, *args, **kwargs):
    return _template_operator('sign({x})', 'sign', np.sign, item, convert_to_float=True, args=args, kwargs=kwargs)


def exp(item, *args, **kwargs):
    return _template_operator('exp({x})', 'exp', np.exp, item, convert_to_float=True, args=args, kwargs=kwargs)


def log(item, *args, **kwargs):
    return _template_operator('log({x})', 'log', np.log, item, convert_to_float=True, args=args, kwargs=kwargs)


def log10(item, *args, **kwargs):
    return _template_operator('log10({x})', 'log10', np.log10, item, convert_to_float=True, args=args, kwargs=kwargs)


def sqrt(item, *args, **kwargs):
    return _template_operator('sqrt({x})', 'sqrt', np.sqrt, item, convert_to_float=True, args=args, kwargs=kwargs)


def string(item):
    if isinstance(item, Hierarchy):
        item = item.identifier
    elif hasattr(item, 'hierarchy_type'):
        item = getattr(item, item.hierarchy_type.idname)
    return _template_operator('toString({x})', 'string', str, item, convert_to_float=False)


def lower(item):
    item = string(item)
    return _template_operator('toLower({x})', 'lower', lambda x: x.lower(), item, convert_to_float=False)


def upper(item):
    item = string(item)
    return _template_operator('toUpper({x})', 'upper', lambda x: x.upper(), item, convert_to_float=False)



python_any = any
python_all = all
python_max = max
python_min = min
python_sum = sum


def sum(item, wrt=None, *args, **kwargs):
    return _template_aggregator('sum({x})', 'sum', python_sum, item, wrt, convert_to_float=True, args=args, kwargs=kwargs)


def max(item, wrt=None, *args, **kwargs):
    return _template_aggregator('max({x})', 'max', python_max, item, wrt, convert_to_float=True, args=args, kwargs=kwargs)


def min(item, wrt=None, *args, **kwargs):
    return _template_aggregator('min({x})', 'min', python_min, item, wrt, convert_to_float=True, args=args, kwargs=kwargs)


def all(item, wrt=None, *args, **kwargs):
    return _template_aggregator('all(i in collect({x}) where i)', 'all', python_all, item, wrt, args=args, kwargs=kwargs)


def any(item, wrt=None, *args, **kwargs):
    return _template_aggregator('any(i in collect({x}) where i)', 'any', python_any, item, wrt, args=args, kwargs=kwargs)


def count(item, wrt=None, *args, **kwargs):
    return _template_aggregator('count({x})', 'count', len, item, wrt, allow_hiers=True, args=args, kwargs=kwargs)


def std(item, wrt=None, *args, **kwargs):
    return _template_aggregator('stDev({x})', 'std', np.std, item, wrt, convert_to_float=True, args=args, kwargs=kwargs)


class Dissociated(FrozenQuery):
    def __init__(self, handler, branch: Branch, variable: CypherVariable, parent: 'FrozenQuery' = None):
        super().__init__(handler, branch, parent)
        self.variable = variable

    def _filter_by_boolean(self, boolean_filter: 'FrozenQuery'):
        new = self._make_filtered_branch(boolean_filter)
        return self.__class__(self.handler, new, self.variable, self)

    def __getitem__(self, boolean_filter: 'Dissociated'):
        if not isinstance(boolean_filter, Dissociated):
            raise TypeError(f"Factors may only be filtered with `[]` using a boolean filter")
        return self._filter_by_boolean(boolean_filter)

    def _apply_aligning_func(self, string, other: 'Dissociated' = None):
        if other is not None:
            if isinstance(other, Dissociated):  # now we have to align first
                aligned = self.branch.align(other.branch)
                inputs = {
                    'x': aligned.action.transformed_variables.get(self.variable, self.variable),
                    'y': aligned.action.transformed_variables.get(other.variable, other.variable)
                }
            elif isinstance(other, FrozenQuery):
                raise TypeError(f"Cannot compare types {self.__class__} and {other.__class__}")
            else:
                aligned = self.branch.add_data(other)
                inputs = {'x': self.variable, 'y': aligned.current_variables[0]}
        else:  # only one variable
            inputs = {'x': self.variable}
            aligned = self.branch
        newbranch = aligned.operate(string, **inputs)
        return Dissociated(self.handler, newbranch, newbranch.current_variables[-1], self)

    def __add__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} + {y}', other)

    def __sub__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} - {y}', other)

    def __mul__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} * {y}', other)

    def __truediv__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} / {y}', other)

    def __pow__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} ^ {y}', other)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__
    __rpow__ = __pow__

    def __neg__(self) -> 'Dissociated':
        return self._apply_aligning_func('(-{x})')

    def __abs__(self) -> 'Dissociated':
        return abs(self)

    def __floor__(self) -> 'Dissociated':
        return floor(self)

    def __ceil__(self) -> 'Dissociated':
        return ceil(self)

    def __round__(self, n=None):
        return round(self, n)

    def __eq__(self, other: Union['Dissociated', int, float, str]) -> 'Dissociated':
        string = '{x} = {y}'
        if isinstance(other, str):
            if is_regex(other):
                string = '{x} =~ {y}'
                other = other.strip('/')
        return self._apply_aligning_func(string, other)

    def __ne__(self, other: Union['Dissociated', int, float, str]) -> 'Dissociated':
        string = '{x} <> {y}'
        if isinstance(other, str):
            if is_regex(other):
                string = 'NOT ({x} =~ {y})'
                other = other.strip('/')
        return self._apply_aligning_func(string, other)

    def __lt__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} < {y}', other)

    def __le__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} <= {y}', other)

    def __gt__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} > {y}', other)

    def __ge__(self, other: Union['Dissociated', int, float]) -> 'Dissociated':
        return self._apply_aligning_func('{x} >= {y}', other)

    def __and__(self, other: 'Dissociated') -> 'Dissociated':
        return self._apply_aligning_func('({x} AND {y})', other)

    def __or__(self, other: 'Dissociated') -> 'Dissociated':
        return self._apply_aligning_func('({x} OR {y})', other)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if len(inputs) != 1:
            raise NotImplementedError(f"Can only translate numpy methods that have 1 argument")
        if method == '__call__':
            return _template_operator(f'{ufunc.__name__}({{x}})', ufunc.__name__, ufunc, self, True, True)
        if method == 'reduce':
            translate = {'add': sum, 'logical_or': any, 'logical_and': all, 'minimum': min, 'maximum': max}[ufunc.__name__]
            return translate(self, wrt=kwargs['axis'])
        else:
            raise NotImplementedError(f"Can only translate numpy methods that are called using __call__ or reduce. Not {method}")

    def _post_process(self, result: py2neo.database.Cursor, squeeze: bool = True) -> Table:
        df = result.to_data_frame()
        assert len(df.columns) == 1
        vs = df.iloc[:, 0].values
        if squeeze and len(vs) == 1:
            return vs[0]
        return vs

    def _prepare_query(self) -> CypherQuery:
        with super()._prepare_query() as query:
            return query.returns(self.variable)