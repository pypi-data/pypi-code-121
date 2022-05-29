import functools as ft
import typing as typ
import numpy as np
import pandas as pd

import pyomo.environ as pyo
from pyomo.core.expr.numvalue import nonpyomo_leaf_types
from pyomo.core.expr import current as EXPR
from pyomo.core.base.var import IndexedVar
from pyomo.opt import TerminationCondition
from pyomo.core.expr.logical_expr import InequalityExpression
from pyomo.core.expr.current import ExpressionBase
from pyomo.core.base.param import IndexedParam, ScalarParam

from .elements import LineItem, MultiLineItem
from .base import PERIODS_TO_STRF

"""
Custom Expressions
--------------------------------------
"""
def model_finder(expr):
    if hasattr(expr, 'parent_block'):
        model = expr.parent_block()
    else:
        if hasattr(expr, 'args'):
            for item in expr.args:
                if  hasattr(item, 'parent_block'):
                    model = item.parent_block()
                    break
    
    return model

def prior(expr, *args, **kwargs):
    model = model_finder(expr)
    return PriorExpression(expr, model, *args, **kwargs)

def cumsum(expr, *args, **kwargs):
    model = model_finder(expr)
    return CumSumExpression(expr, model, *args, **kwargs)

def mean(expr, *args, **kwargs):
    model = model_finder(expr)
    return MeanExpression(expr, model, *args, **kwargs)

class MethodExpression(ExpressionBase):
    """
    https://pyomo.readthedocs.io/en/latest/developer_reference/expressions/managing.html#walking-an-expression-tree-with-a-visitor-class
    """
    PRECEDENCE = 0

    def __init__(self, expr, model, index=None):
        super().__init__((expr,))
 
        self._root_expr = expr
        self._model = model
        self._index = index # required only for testing; arg passed to "create_node" should have the period from `periodize`

    def set_index(self, index):
        self._index = index

    def set_model(self, model):
        self._model = model # backdoor to update expression during model construction ... without, certain parameters are not initialized by the time expressino is evauluated

    def nargs(self):
        return 1 # target node is the only argument

    def _compute_polynomial_degree(self, result):
        return result[0]
    
    def _apply_operation(self, result):
        return result

class CumSumExpression(MethodExpression):    
    def create_node_with_local_data(self, args, classtype=None):
        """
        Returns cumulative summation of the indexed variable up to the period specified.
        """
        assert classtype is None
        arg = args[0]
        if arg is self._root_expr: # this SHOULD only be used when testing; args passed should be same as __init__
            indexed = getattr(self._model, f'{arg.name}_periods')
        else:
            indexed = getattr(self._model, arg.name.split("[")[0]) # here, arg is single value so must find full IndexedVariable from whence it came
        
        last = self._model.periods.ord(self._index) + 1
        node = sum(indexed[self._model.periods.at(i)] for i in range(1, last))
        
        return node

def compound_growth(base, growth_rate, n):
    #### SHOULD BE AN EXPRESSION!!!!!####
    factors = np.repeat(1 + growth_rate, n).cumprod()
    return base*factors

class CompoundGrowthExpression(MethodExpression):
    def create_node_with_local_data(self, args, classtype=None):
        """
        Returns cumulative summation of the indexed variable up to the period specified.
        """
        assert classtype is None

        arg = args[0]
        if arg is self._root_expr: # this SHOULD only be used when testing; args passed should be same as __init__
            indexed = getattr(self._model, f'{arg.name}_periods')
        else:
            indexed = getattr(self._model, arg.name.split("[")[0]) # here, arg is single value so must find full IndexedVariable from whence it came
        
        last = self._model.periods.ord(self._index) + 1
        node = sum(indexed[self._model.periods.at(i)] for i in range(1, last))
        
        return node

class PriorExpression(MethodExpression):
    """
    https://pyomo.readthedocs.io/en/latest/developer_reference/expressions/managing.html#walking-an-expression-tree-with-a-visitor-class
    """
    PRECEDENCE = 20

    def __init__(self, expr, model, short_name, index=None):
        super().__init__(expr, model, index=index)
 
        self._short_name = short_name
    
    def create_node_with_local_data(self, args, classtype=None):
        """
        Returns cumulative summation of the indexed variable up to the period specified.
        """
        assert classtype is None

        node = args[0]

        iloc = self._model.periods.ord(self._index)
        indexed = getattr(self._model, f'{self._short_name}_periods')
        if iloc != 1: # if the period is the first period, there is no prior period
            node = node + indexed[self._model.periods.at(iloc - 1)] # for every period other than the first period, get the prior period
                    
        return node

class MeanExpression(MethodExpression):
    """
    https://pyomo.readthedocs.io/en/latest/developer_reference/expressions/managing.html#walking-an-expression-tree-with-a-visitor-class
    """
    PRECEDENCE = 20

    def mean(self, t1, t2):
        return (t1 + t2) / 2

    def create_node_with_local_data(self, args, classtype=None):
        """
        Returns cumulative summation of the indexed variable up to the period specified.
        """
        assert classtype is None

        arg = args[0]
        if arg is self._root_arg: # this SHOULD only be used when testing; args passed should be same as __init__
            indexed = getattr(self._model, f'{arg.name}_periods')
        else:
            indexed = getattr(self._model, arg.name.split("[")[0]) # here, arg is single value so must find full IndexedVariable from whence it came
        
        node = args[0]
        iloc = self._model.periods.ord(self._index)
        if iloc == 1: # if the period is the first period, there is no prior period
            node = self.mean(indexed[self._model.periods.at(iloc)], 0)
        else:
            node = self.mean(indexed[self._model.periods.at(iloc)], indexed[self._model.periods.at(iloc - 1)])  # for every period other than the first period, get the prior period
                    
        return node

def total(expr, *args, **kwargs):
    model = model_finder(expr)
    return TotalExpression(expr, model, *args, **kwargs)

class TotalExpression(MethodExpression):
    PRECEDENCE = 20

    def create_node_with_local_data(self, args, classtype=None):
        """
        Returns cumulative summation of the indexed variable up to the period specified.
        """
        assert classtype is None

        node = args[0]
        indexed = getattr(self._model, node.name.split("[")[0]) 
        period = self._index[-1]
        nidxs = len(self._index) - 1
        sliced = (slice(None, None, None),)*nidxs

        return sum(v for v in indexed[sliced, period])

class PeriodizeVisitor(EXPR.ExpressionReplacementVisitor):
    """
    Transforms expressions with ScalarVar to expression using thei IndexedVar / Param derivatives
    """
    def __init__(self, model, index):
        super().__init__()
        self.model = model
        self.index = index

    def periodize_args(self, args):
        for arg in args:
            if type(arg) not in nonpyomo_leaf_types and arg.is_component_type() and not arg.is_indexed():
                if hasattr(self.model, f'{arg.name}_periods'):
                    indexed = getattr(self.model, f'{arg.name}_periods')
                    if indexed.dim() == 1: # if component only has 1 dimension, then that dimension should be the period
                        yield indexed[self.index[-1]]
                    else:
                        yield indexed[self.index]
                else:
                    scalar = getattr(self.model, f'{arg.name}') # have to swap out the AbstractModel Param for the Concrete Param
                    yield scalar
            else:
                yield arg
        
    def enterNode(self, node):
        args = list(self.periodize_args(node.args))
        return args, [False, args]

    def acceptChildResult(self, node, data, child_result, child_idx):
        if data[1][child_idx] is not child_result:
            data[1][child_idx] = child_result
            data[0] = True
        return data
    
    def exitNode(self, node, data):
        if hasattr(node, 'set_index'):
            node.set_index(self.index)
            node.set_model(self.model)  # backdoor to update expression during model construction ... without, certain parameters are not initialized by the time expressino is evauluated
        return node.create_node_with_local_data(tuple(data[1]))

class Where:
    """
    Handler for 
    """
    def __init__(self, mngr, tgt_name, inequal=None, big_M=1000):
        self.M = mngr
        self.short_name = tgt_name
        self.big_M = big_M

        if inequal is not None:
            self.parse_inequal(inequal)

    @property
    def target(self):
        return f'{self.short_name}_periods'

    @property
    def delta(self):
        return f'delta_{self.short_name}_periods'
    
    @property
    def comp(self):
        return f'{self._comp.name}_periods'

    @property
    def op(self):
        return self._op

    @property
    def c1(self):
        return f'{self.short_name}_constraints1'

    @property
    def c2(self):
        return f'{self.short_name}_constraints2'

    @property
    def c3(self):
        return f'{self.short_name}_constraints3'

    @property
    def constraints(self):
        return self.c1, self.c2, self.c3

    def parse_inequal(self, inequal):
        if not isinstance(inequal, InequalityExpression):
            raise ValueError('`where` can only accept `InequalityExpression` objects of form `x<0,x<=0,x>0,x>=0`')

        if inequal.strict:
            raise ValueError("currently `where` does not support 'strict' inequalities")

        _l, _r = inequal.args
        self._comp = _l if isinstance(_r, int) else _r
        self._op = 'le' if isinstance(_r, int)  else 'ge'
        self._inequal = inequal

    def ge_exprs(self, period):
        return {
            'c1': self.target[period] - self.big_M * self.delta[period] <= 0,
            'c2': self.comp[period] - self.target[period] <= 0,
            'c3': self.comp[period] - self.target[period] + self.big_M * self.delta[period] <= self.big_M
        }

    def ge_rules(self):
        return [ge_r1, ge_r2, ge_r3]

    def le_exprs(self, period):
        return {
            'c1': self.target[period] - self.big_M * self.delta[period] <= 0,
            'c2': -self.target[period] - self.comp[period] <= 0,
            'c3': self.comp[period] - self.target[period] + self.big_M * self.delta[period] <= self.big_M
        }

    def le_rules(self):
        return [le_r1, le_r2, le_r3]

    def exprs(self, period):
        if self.op == 'ge':
            return self.ge_exprs(period)
        elif self.op == 'le':
            return self.le_exprs(period)

    def rules(self):
        if self.op == 'ge':
            return self.ge_rules()
        elif self.op == 'le':
            return self.le_rules()

    def assign_vars(self):
        self.M.setvar(self.short_name) # root attribute i  s a shadow used to generate expressions; must be Var to allow for expressions
        self.M.setvar( # assign the IndexedParam; this contains actual data and is used in expression transformation
            f'{self.short_name}_periods',
            self.M.abstract.periods,
            domain=pyo.NonNegativeReals
        )
        self.M.setvar(f'delta_{self.short_name}') # root attribute i  s a shadow used to generate expressions; must be Var to allow for expressions
        self.M.setvar( # assign the IndexedParam; this contains actual data and is used in expression transformation
            f'delta_{self.short_name}_periods',
            self.M.abstract.periods,
            domain=pyo.Binary
        )

    def assign_exprs(self):
        for constr, rule in zip(self.constraints, self.rules()):
            rule = rule_factory(rule, self.target, self.comp, self.delta, self.big_M)
            setattr(self.M.abstract, constr, pyo.Constraint(self.M.abstract.periods, rule=rule))

def ge_r1(M, p, tgtstr, compstr, deltastr, big_M):
    target = getattr(M, tgtstr)
    delta = getattr(M, deltastr)
    return target[p] - big_M * delta[p] <= 0

def ge_r2(M, p, tgtstr, compstr, deltastr, big_M):
    target = getattr(M, tgtstr)
    comp = getattr(M, compstr)
    return comp[p] - target[p] <= 0

def ge_r3(M, p, tgtstr, compstr, deltastr, big_M):
    target = getattr(M, tgtstr)
    comp = getattr(M, compstr)
    delta = getattr(M, deltastr)
    return comp[p] - target[p] + big_M * delta[p] <= big_M

le_r1 = ge_r1

def le_r2(M, p, tgtstr, compstr, deltastr, big_M):
    target = getattr(M, tgtstr)
    comp = getattr(M, compstr)
    return -target[p] - comp[p] <= 0

le_r3 = ge_r3

def periodize(M, idx, tgtstr, expr):
    tgt = getattr(M, f'{tgtstr}_periods')
    walker = PeriodizeVisitor(M, idx)
    expr = walker.walk_expression(expr)
    return tgt[idx] == expr

def total(M, p, tgtstr):
    base = getattr(M, f'{tgtstr}_periods')
    tgt = getattr(M, f'tot_{tgtstr}_periods')
    
    sliced = (slice(None, None, None),)*(base.dim() - 1)
    return tgt[p] == sum(base[sliced, p])

def rule_factory(func, *args):
    @ft.wraps(func)
    def wrapper(M, *idx_args):
        return func(M, idx_args, *args)
    return wrapper

class obj_factory:
    def __init__(self, func, target=None):
        ft.update_wrapper(self, func)
        self.func = func
        self.target= target

    def __call__(self, *args):
        return self.func(*args, target=self.target)

class ModelManager:
    def __init__(self, stat, abstract=None):
        self.stat = stat
        if abstract is None:
            self._init_model()
        else:
            self.abstract = abstract
            
        self.solver = pyo.SolverFactory('glpk')

    def __getattribute__(self, name:str) -> typ.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            try:
                model = object.__getattribute__(self, '_model')
                return object.__getattribute__(model, name)
            except AttributeError:
                pass

            raise e

    @property
    def obj_assigned(self):
        return hasattr(self.abstract, 'obj')

    @property
    def has_instance(self):
        return hasattr(self, '_instance')

    @property
    def periods(self):
        return self.get('periods')

    def update_stat(self, stat):
        self.stat = stat

    def get(self, name):
        if self.has_instance:
            return getattr(self.instance, name)
        else:
            return getattr(self.abstract, name)

    def instance_data(self):
        root = {None: {}}
        data = root[None]
        data['periods'] = self.stat.periods.strftime(PERIODS_TO_STRF[self.stat.periods.freqstr]).tolist()
        
        if hasattr(self.abstract, 'multi'):
            aligned = self.stat.accounts.align(self.stat.by, with_item=True).strf_columns().drop_item_level()
            self._grouped_index = aligned[0].index
            self._has_multi = True
            data['multi'] = self._grouped_index.values.tolist()
        else:
            self._has_multi = False

        for var in self.abstract.component_objects(pyo.Param):
            name = var.name.split('_periods')[0]
            node = self.stat.G.nodes[name]
            if isinstance(var, IndexedParam):
                if node['is_multi']:
                    obj = aligned[name]
                    vardata = {}
                    for grouping, row in obj.iterrows():
                        grouping = (grouping, ) if isinstance(grouping, (str, int, float)) else grouping # handle single category groupbys
                        for period, val in row.iteritems():
                            vardata[(*grouping, period)] = val
                    data[var.name] = vardata
                else:
                    node = self.stat.G.nodes[name]
                    obj = node['obj']() if callable(node['obj']) else node['obj']
                    data[var.name] = {idx: v for idx, v in zip(data['periods'], obj)}
            else:
                if isinstance(var, ScalarParam) and node['nodetype'] == 'factor':
                    data[var.name] = {None: node['obj']}
                elif isinstance(var, ScalarParam) and node['nodetype'] == 'account':
                    data[var.name] = {None: 0}
                
        return root

    def _init_model(self):
        self.abstract = pyo.AbstractModel()
        self.abstract.periods = pyo.Set()

    def set_multi_index(self):
        if not self.has_multi_index():
            self.abstract.multi = pyo.Set()

    def has_multi_index(self):
        return hasattr(self.abstract, 'multi')

    def index_args(self, is_multi:bool):
        if is_multi:
            args = (self.abstract.multi, self.abstract.periods)
        else:
            args = (self.abstract.periods,)
        return args

    def setparam(self, name, *args, is_multi=False, mutable:bool=True, **kwargs):
        if '_periods' in name:
            args = (*self.index_args(is_multi), *args)
        setattr(self.abstract, name, pyo.Param(*args, **kwargs, mutable=mutable, domain=pyo.Reals))

    def setvar(self, name, *args, domain=pyo.Reals, **kwargs):
        setattr(self.abstract, name, pyo.Var(*args, **kwargs, domain=domain))

    def periodize(self, tgt, expr, is_multi:bool=False):
        rule = rule_factory(periodize, tgt, expr)
        setattr(self.abstract, f'{tgt}_constraints', pyo.Constraint(*self.index_args(is_multi), rule=rule))

    def total(self, comp):
        rule = rule_factory(total, comp.name)
        setattr(self.abstract, f'tot_{comp.name}_constraints', pyo.Constraint(self.abstract.periods, rule=rule))

    def where(self, *args, **kwargs):
        return Where(self, *args, **kwargs)

    def assign_vars(self, short_name, is_multi:bool=False):
        self.setvar(short_name) # root attribute is a shadow used to generate expressions; must be Var to allow for expressions
        self.setvar(f'{short_name}_periods', *self.index_args(is_multi))

    def assign_objective(self, target:str=None):
        if target is None:
            target = next(self._iter_indexed_vars())
        else:
            target = getattr(self.abstract, f'{target}_periods')

        if hasattr(self.abstract, 'obj'):
            self.abstract.del_component('obj')

        def rule(M, *args, target=None):
            if isinstance(target, str):
                target = getattr(M, target)
            return pyo.summation(target)

        rule = obj_factory(rule, target=target)
        self.abstract.obj = pyo.Objective(rule=rule, sense=pyo.maximize)

    def _update_param(self, name, key, value):
        param = getattr(self.instance, f'{name}_periods') ### Updates happen on instantiated models

        if isinstance(key, (str, int, float)):
            param[key] = value
        else:
            for k, v in zip(key, value):
                param[k] = v

    def _iter_indexed_vars(self, instance=False):
        model = self.instance if instance else self.abstract
        for var in model.component_objects(pyo.Var):
            if isinstance(var, IndexedVar):
                yield var

    def _iter_indexed_params(self):
        for var in self.instance.component_objects(pyo.Param):
            if isinstance(var, IndexedParam):
                yield var

    def create_instance(self):
        self.stat.close_model_context()
        data = self.instance_data()
        self.stat.open_model_context()
        self.instance = self.abstract.create_instance(data)

    def solve(self):
        from .elements.elements import index_values
        self.results = self.solver.solve(self.instance)

        msg = 'Your model does not have an optimal solution.'
        msg += ' See stat.M.results and stat.M.model.pprint to debug.'
        assert self.results.solver.termination_condition is TerminationCondition.optimal, msg

        for var in self._iter_indexed_vars(instance=True):
            node = self.stat.graph.nodes[var.name.split('_periods')[0]]
            values = np.array([pyo.value(var[idx]) for idx in var.keys()])
            if node['is_multi']:
                values = values.reshape(-1, self.stat.periods.size)
                node['obj'] = MultiLineItem(values, index=self._grouped_index, columns=self.stat.periods, short_name=node['short_name'], name=node['name'], graph=self.stat.graph)            
            elif node['is_total'] or self._has_multi:
                values = values.reshape(-1, self.stat.periods.size)
                index = index_values(self._grouped_index, placeholder='---')
                if isinstance(index, str):
                    index = (index, ) # if only one level, must make a tuple
                index = pd.MultiIndex.from_tuples((index,), names=self._grouped_index.names)
                node['obj'] = MultiLineItem(values, index=index, columns=self.stat.periods, short_name=node['short_name'], name=node['name'], graph=self.stat.graph)            
            else:
                node['obj'] = LineItem(values, index=self.stat.periods, short_name=node['short_name'], name=node['name'], graph=self.stat.graph)            
             
        return self.results
