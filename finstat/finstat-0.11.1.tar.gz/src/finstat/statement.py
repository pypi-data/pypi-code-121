import functools as ft
import warnings
import typing as typ
import numpy as np
import pandas as pd

import networkx as nx

from .base import FinStatBaseObject, PERIODS_TO_STRF
from .elements import LineItem, MultiLineItem, Elements, Schedule, ScheduleFunction, ScheduleFactory

from .functions.base import StatFunction
from .optimize import ModelManager
from .groupers import FinStatResampler, FinStatGroupBy
from .valuation import Valuation

NODE_TYPES = np.array(['factor', 'time-series-factors', 'statement', 'schedule', 'account', 'metric'])
EXCLUDED_NODES = NODE_TYPES[:-2]
LINEITEM_NODES = NODE_TYPES[-2:]
NON_FACTOR_NODES = NODE_TYPES[1:]
REQUIRED_NODE_ATTRIBUTES = [
    'obj', 'name', 'short_name', 'statement', 
    'nodetype', 'is_input', 'is_multi', 'is_total', 'model', 'expr', 
    'position', 'insert_after', 'hide'
    ]

FinancialStatementType = typ.TypeVar('FinancialStatementType', bound='FinancialStatement')

class ModelContextManager:
    def __init__(self, stat, target:str=None, solve:bool=True, new_instance:bool=False, *args, **kwargs):
        self.stat = stat
        self._solve = solve
        self._new_instance = new_instance

        self._tgtstr = target

    @property
    def M(self):
        return self.stat.M

    def assign_objective(self, target):
        self._tgtstr = target
        self.M.assign_objective(self._tgtstr)

    # Utility functions to update graph attributes
    def update_node_expr(self, expr, short_name):
        self.stat.G.nodes[short_name]['expr'] = expr

    def add_nodeholder(self, 
        name, 
        short_name, 
        model,
        is_multi=False,
        is_total=False,
        hide=False, 
        insert_after=None,
        ):
        """
        Creates model attributes, constraints, and graph node associated with a new metric.

        Both the expression and the finalized object can be appended at any point
        """
        self.stat.G.add_node(
            short_name,
            obj=None,
            name=name,
            short_name=short_name,
            statement=self.stat.short_name,
            model=model,
            expr=None,
            nodetype='metric',
            is_input=False,
            is_multi=is_multi,
            is_total=is_total,
            hide=hide,
            position=self.stat.G.find_node_position(insert_after),
            insert_after=insert_after,
        )

    # User-exposed full operations #
    def as_periods(self, expr=None, construct:bool=True, assign:bool=True, short_name=None, is_multi=False, **kwargs):
        # turns the single ScalarVar expression into a list of IndexedVar expressions for each period
        # and adds each expression to corresponding constraint
        # expression added to the existing node;
        # this is the expr BEFORE the periodize transformation
        if isinstance(expr, str) and 'name' not in kwargs:
            raise ValueError('If you do not provide `expr` because `assignt=False` you must provide `name` as kwarg')

        if not construct and short_name is None:
            raise ValueError('When `construct=False`, you must provide `short_name` in order to identify the already constructed node.')

        if short_name is None and 'name' in kwargs:
            short_name = self.stat._shorten(kwargs['name'])

        if construct and not self.stat.has_node(short_name):
            if not self.stat.no_model:
                self.M.assign_vars(short_name, is_multi=is_multi) # instantiate model relations (root Var, IndexedVar, Constraint List)
                model = self.M.get(short_name)
            else:
                model = 1 # when it is called, allows model attribute to be added to another
            self.add_nodeholder(short_name=short_name, is_multi=is_multi, model=model, **kwargs) # add corresponding node (with expr=None)

        if assign:
            assert expr is not None
            if not self.stat.no_model:
                self.M.periodize(short_name, expr, is_multi=is_multi) # periodize model expressions and assign constraints
                self.update_node_expr(expr, short_name) # update node for the regular expression on the root Vars / Params

    def as_multi(self, *args, **kwargs):
        self.as_periods(*args, is_multi=True, **kwargs)

    def as_total(self, comp, construct:bool=True, assign:bool=True, short_name=None, **kwargs):
        # if isinstance(expr, str) and 'name' not in kwargs:
        #     raise ValueError('If you do not provide `expr` because `assign=False` you must provide `name` as kwarg')

        if not construct and short_name is None:
            raise ValueError('When `construct=False`, you must provide `short_name` in order to identify the already constructed node.')

        if short_name is None:
            short_name = f'tot_{comp.name}'

        if construct and not self.stat.has_node(short_name):
            self.M.assign_vars(short_name, is_multi=False) # instantiate model relations (root Var, IndexedVar, Constraint List)
            self.add_nodeholder(short_name=short_name, is_multi=False, is_total=True, **kwargs) # add corresponding node (with expr=None)

        if assign:
            self.M.total(comp) # periodize model expressions and assign constraints
            self.update_node_expr(comp, short_name) # update node for the regular expression on the root Vars / Params

    def where(self, expr=None, big_M=1000, construct:bool=True, assign:bool=True, short_name=None, **kwargs):
        if isinstance(expr, str) and 'name' not in kwargs:
            raise ValueError('If you do not provide `expr` because `assignt=False` you must provide `name` as kwarg')

        if not construct and short_name is None:
            raise ValueError('When `construct=False`, you must provide `short_name` in order to identify the already constructed node.')

        if short_name is None and 'name' in kwargs:
            short_name = self.stat._shorten(kwargs['name'])

        where = self.M.where(short_name, big_M=big_M) # instantiate constructor only
         
        if construct and not self.stat.has_node(short_name):
            where.assign_vars()

            self.add_nodeholder(**kwargs) # actual node

            kwargs['name'] = 'delta_' + kwargs['short_name']
            kwargs['short_name'] = kwargs['name']
            self.add_nodeholder(**kwargs) # delta node

        if assign:
            where.parse_inequal(expr)
            where.assign_exprs()
            self.update_node_expr(expr, short_name)

    def __call__(self, *args, **kwargs):
        self.as_periods(*args, **kwargs)

    def __enter__(self):
        self.stat.open_model_context() # Open model context so that the statement attributes return Pyomo expressions
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type:
                raise exc_type(exc_value) # preempt other operations by raising any incoming exception
            
            if not self.stat.no_model:
                if not self.M.obj_assigned:
                    self.M.assign_objective(self._tgtstr)
                
                if self._new_instance or not self.M.has_instance:
                    self.M.create_instance()

                if self._solve:
                    self.M.solve()
        finally:
            self.stat.close_model_context() # Flag must be closed after calculation to ensure LineItem objects can be used normally

class StatGraph:
    REQUIRED_ATTRS = REQUIRED_NODE_ATTRIBUTES
    NODE_TYPES = NODE_TYPES

    def __init__(self, stat:FinancialStatementType, graph:nx.Graph):
        self._stat = stat
        self._graph = graph # each statement has its own StatGraph, but all sub-statements shared the same nx Graph

    def __getattribute__(self, name:str) -> typ.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            try:
                graph = object.__getattribute__(self, '_graph')
                return object.__getattribute__(graph, name)
            except AttributeError:
                pass

            raise e

    def add_node(self, node:str, **kwargs):
        """
        Centralizes `add_node` to ensure each node receives the same attributes.
        """
        not_provided = [attr for attr in self.REQUIRED_ATTRS if attr not in kwargs]
        assert not not_provided, f'`add_node` has missing parameters: {", ".join(not_provided)}'
        extra_provided = [k for k in kwargs.keys() if k not in self.REQUIRED_ATTRS]
        assert not extra_provided, f'`add_node` given extra parameters: {", ".join(extra_provided)}'

        self._graph.add_node(node, **kwargs)

    ### GRAPH FILTERING ###
    def filter_subgraph(self, attr, value, statname):
        # returns a subgraph containing only the nodes with attribute value specified
        graph = self._graph
        def filter_stat(n):
            return graph.nodes(data='statement')[n] == statname
        
        def f(n):
            if hasattr(value, '__len__') and not isinstance(value, str):
                return graph.nodes(data=attr)[n] in value
            else:
                return graph.nodes(data=attr)[n] == value

        if statname in graph.nodes: # if the statement caller is a node, then it is a sub-statement and we want to filter the graph to just that 
            statgraph = nx.subgraph_view(graph, filter_node=filter_stat)
            return nx.subgraph_view(statgraph, filter_node=f)
        else:
            return nx.subgraph_view(graph, filter_node=f)
    
    def filter_graph_by_attribute(self, attr, value):
        return self.filter_subgraph(attr, value, self._stat.short_name)

    def filter_graph_by_attributes(self, **kwargs):
        for k, v in kwargs.items():
            graph = self.filter_graph_by_attribute(k, v)
        return graph

    def filter_nodes_by_attribute(self, attr, value, return_node:bool=False, return_tuple:bool=False, **kwargs):
        for node in self.filter_subgraph(attr, value, self._stat.short_name).nodes(**kwargs):
            if return_node:
                yield self._graph.nodes[node]
            else:
                node = node[1] if isinstance(node, tuple) and not return_tuple else node
                if 'data' in kwargs and kwargs['data'] == 'obj':
                    if isinstance(node, tuple):
                        yield node[0], node[1]() if callable(node[1]) else node[1] # calls the ScheduleFunction
                    else:
                        yield node() if callable(node) else node
                else:
                    yield node

    def filter_nodes_by_attributes(self, return_tuple=False, **kwargs):
        filter_kwargs = {k: v for k, v in kwargs.items() if k in self.REQUIRED_ATTRS}
        kwargs = {k: v for k, v in kwargs.items() if k not in filter_kwargs}
        graph = self.filter_graph_by_attributes(**filter_kwargs)

        for node in graph.nodes(**kwargs):
            node = node[1] if isinstance(node, tuple) and not return_tuple else node
            if 'data' in kwargs and kwargs['data'] == 'obj':
                yield node() if callable(node) else node # calls the ScheduleFunction
            else:
                yield node

    ### POSITION MANAGEMENT ###
    @property
    def node_positions(self):
        return np.array(list(nx.get_node_attributes(self._graph, 'position').values()))

    @property
    def next_node_position(self):
        if self.node_positions.size == 0:
            return 0
        else:
            return self.node_positions.max() + 1

    def get_node_position(self, name):
        """
        Returns order attribute of node
        """
        return self._graph.nodes[name]['position']

    def update_node_positions(self, insert_pos:int):
        old_order = self.node_positions
        new_order = np.where(old_order >= insert_pos, old_order + 1, old_order)
        for name, position in zip(list(self._graph.nodes), new_order):
            self._graph.nodes[name]['position'] = position

    def find_node_position(self, insert_after:typ.Union[str, None]):
        if insert_after is None:
            order = self.next_node_position
        else:
            order = self.get_node_position(insert_after) + 1
            self.update_node_positions(order)

        return order

class ViewManager:
    SUPPORTED_VIEWS = ['visible', 'hidden', 'all']
    NODE_TYPES = NODE_TYPES
    EXCLUDED_NODES = EXCLUDED_NODES
    LINEITEM_NODES = LINEITEM_NODES

    def __init__(self, stat:FinancialStatementType):
        self._stat = stat
        self._viewstr = 'visible'

    def set_view(self, viewstr:str):
        if self._viewstr not in self.SUPPORTED_VIEWS:
            raise ValueError(f"`viewstr` must be one of {', '.join(self.SUPPORTED_VIEWS)}")

        self._viewstr = viewstr

    def visible(self):
        self.set_view('visible')
        return self._stat

    def all(self):
        self.set_view('all')
        return self._stat

    def get_visible(self):
        filters = dict(nodetype=ViewManager.LINEITEM_NODES, statement=self._stat.short_name, hide=False)
        return Elements(*self._stat.G.filter_nodes_by_attributes(data='obj', **filters))

    def get_all(self):
        filters = dict(nodetype=self.LINEITEM_NODES, statement=self._stat.short_name)
        return Elements(*self._stat.G.filter_nodes_by_attributes(data='obj', **filters))

    def __call__(self):
        """
        Attribute manages the contents of `to_frame` output
        """
        return getattr(self, f'get_{self._viewstr}')()

class FinancialStatement(FinStatBaseObject):
    """
    Main class
    
    Consists of DataFrame front-end, matrix backend?,
    and graph structure to map front-end on to backend,
    graph structure used to facilitate observer pattern
    and automatic updates

    Financial statement as a directed graph
    Each LineItem / Metric / Ratio is a node
    LineItem objects never have predecessors
    Metric objects must have predecssors

    Each account is assigned to a 
            self.graph.add_node(account.short_name, obj=account)

    Parameters:
        periods: pd.PeriodIndex
            time-series applied to all the constituent lineitems
    """
    _metadata = ['_name', '_short_name', '_graph']
    EXCLUDED_NODES = EXCLUDED_NODES
    LINEITEM_NODES = LINEITEM_NODES
    _ipython_canary_method_should_not_exist_ = None # Need for ipython support of __getattribute__ customization

    def __init__(self, 
        periods:pd.PeriodIndex=None, 
        name:str=None,
        short_name:str=None,
        groupby:typ.Iterable[str] | str=[],
        graph:nx.DiGraph=None,
        no_model:bool=False,
        ):
        if graph is None:
            graph = nx.DiGraph(
                stat=self,
                OPEN_MODEL_CONTEXT=False,
                periods=periods,
                no_model=no_model,
                by=[groupby] if isinstance(groupby, str) else groupby # this can be access by any object with the graph as an attribute
            )
        
        super().__setattr__('_graph', StatGraph(self, graph))
        super().__setattr__('_name', name)
        super().__setattr__('_short_name', self._shorten(name, short_name))
        super().__setattr__('_view_mngr', ViewManager(self))

        if 'model_mngr' not in self._graph.graph:
            self._graph.graph['model_mngr'] = ModelManager(self)

        super().__setattr__('RELATED', [])

    @property
    def _constructor(self):
        return FinancialStatement

    def __getattribute__(self, name:str) -> typ.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            try:
                graph = object.__getattribute__(self, 'G')
                nodes = graph.__getattribute__('nodes')
                if name in nodes:
                    AS_EXPR = object.__getattribute__(self, 'AS_EXPR') ### when AS_EXPR, the pyomo model version of the node attribute is passed
                    if AS_EXPR:
                        return nodes[name]['model']
                    else:
                        obj = nodes[name]['obj']
                        if callable(obj): # if 'obj' is a ScheduleFunction, call the it
                            return obj()
                        else:
                            return obj
            except AttributeError as e:
                raise e

            raise e

    def __setattr__(self, key, value):
        if self.has_node(key):
            node = self.graph.nodes[key]
            if node['nodetype'] == 'factor':
                M_attr = self.M.get(key)
                M_attr = value # assigning the value directly will update the already-initialized Pyomo object (should be a ScalarParam)
                self.solve_out_of_context() # resolve model if there is an objective function
                node['obj'] = value
        elif isinstance(value, (int, float, np.number)):
            self.add_factor(key, value)
        else:
            raise Exception('FinancialStatement objects do not allow attribute assignment except for `factor` nodes')

    def get(self, name):
        if self.model_context_is_open:
            warnings.warn('When `OPEN_MODEL_CONTEXT=True`, `get` returns a pyomo object, not a finstat object')
        return getattr(self, name)

    ### VISUALIZAITON ###
    def __repr__(self):
        return f'FinancialStatement: {self.short_name}'

    def _repr_html_(self):
            if self.is_substat or self.statements.size == 0:
                return self._frame._repr_html_()
            else:
                statstrs = ''
                last = 0
                for i, (short_name, name) in enumerate(zip(self.statements.short_names, self.statements.names)):
                    statstrs += f"""
                        <tr style="text-align: left;">
                        <td>{i + 1}.</td>
                        <td style="text-align: left;">{short_name}</td>
                        <td style="text-align: left;">{name}</td>
                        </tr>
                    """
                    last = i
                for i, related in enumerate(self.RELATED):
                    statstrs += f"""
                        <tr style="text-align: left;">
                        <td>{last + i + 1}.</td>
                        <td style="text-align: left;">{related.short_name}</td>
                        <td style="text-align: left;">{related.name}</td>
                        </tr>
                    """
                return f"""<div>\n
                    <table border="1" class="dataframe">\n  
                    <caption style="text-align: left; font-size: 1.25em; font-weight: bolder;">Statements</caption>
                    <thead>\n    
                    <tr style="text-align: left;">\n
                        <th></th>\n
                        <th style="text-align: left;">Attr</th>\n    
                        <th style="text-align: left;">Name</th>\n
                    </tr>\n
                    </thead>\n  
                    <tbody>\n
                    {statstrs}
                    </tbody>\n
                    </table>\n
                </div>
                """
    
    @property
    def no_model(self):
        return self.G.graph['no_model']

    @property
    def view(self):
        """
        Attribute manages the contents of `to_frame` output
        """
        return self._view_mngr

    @property
    def _frame(self):
        super().__setattr__('__frame__', self.to_frame())
        return self.__frame__

    def to_frame(self, with_periods:bool=True, strftime:str=None, *args, **kwargs) -> pd.DataFrame:
        if self.empty:
            frame = pd.DataFrame([], columns=[f'Empty Statement: {self.name}'])
        elif self.view().size == 0:
            frame = pd.DataFrame([], columns=[f'Empty View: {self.name}'])
        else:
            frame = self.view().concat(*args, by=self.by, **kwargs)

        if not with_periods and isinstance(frame.columns, pd.PeriodIndex):
            if strftime is None:
                strftime = PERIODS_TO_STRF[self.periods.freqstr]
            
            frame.columns = frame.columns.strftime(strftime)

        return frame

    #### Standard Properties ####
    @property
    def name(self):
        return self._name

    @property
    def _periods(self):
        return self.graph.graph['periods']

    @property
    def periods(self):
        return self._periods

    def update_periods(self, periods:pd.PeriodIndex):
        self.graph.graph['periods'] = periods 

    @property
    def empty(self):
        return not self.lineitems.size

    @property
    def by(self):
        return self.graph.graph['by']

    def update_by(self, by:typ.Iterable[str]):
        self.graph.graph['by'] = by

    @property
    def is_substat(self):
        return self.short_name in self.G.nodes # the main statement object will not be a node in the graph; all others will be

    ### Nodes ###
    @property
    def elements(self):
        graph = object.__getattribute__(self, 'G')
        return Elements(*graph.filter_nodes_by_attribute('nodetype', NON_FACTOR_NODES, data='obj'))

    @property
    def statements(self):
        graph = object.__getattribute__(self, 'G')
        return Elements(*graph.filter_nodes_by_attribute('nodetype', 'statement', data='obj'))    

    @property
    def factors(self):
        filters = dict(nodetype='factor')
        if self.is_substat:
            filters['statement'] = self.short_name

        factors = self.G.filter_nodes_by_attributes(data='obj', return_tuple=True, **filters)
        return pd.Series(dict(factors), name='Factors', dtype=object)

    @property
    def schedules(self):
        filters = dict(nodetype='schedule', statement=self.short_name)
        return Elements(*self.G.filter_nodes_by_attributes(data='obj', **filters))

    @property
    def lineitems(self) -> Elements:
        """
        Returns all LineItem objects that are nodes on the FinancialStatement graph. This includes lineitems nested
        in the subgraphs of sections.
        """
        filters = dict(nodetype=self.LINEITEM_NODES)
        return Elements(*self.G.filter_nodes_by_attributes(data='obj', **filters))

    @property
    def accounts(self) -> Elements:
        """
        Returns all LineItem objects that are nodes on the FinancialStatement graph. This includes lineitems nested
        in the subgraphs of sections.
        """
        return Elements(*self.G.filter_nodes_by_attributes(data='obj', nodetype='account'))

    def add_related(self, name, statement):
        # RELATED ARE NOT A PART OF THE GRAPH!!!
        super().__setattr__(name, statement)
        self.RELATED.append(statement)

    def add_statement(self, name, periods=None, insert_after:str=None, **kwargs):
        """
        Adds statement meta to the FinancialStatement
        1. Add statement meta to graph
        2. Add statement `short_name` to `__statements__` (need for lookup in `__getattribute__`)
        3. Assign `short_name` as attribute that simply returns the statement object
        """
        periods = self.periods if periods is None else periods
        stat = FinancialStatement(name=name, graph=self.graph._graph, periods=periods, **kwargs) # pass the underlying nx Graph, NOT the StatGraph

        self.G.add_node(
            stat.short_name,
            obj=stat,
            name=stat.name,
            short_name=stat.short_name,
            statement=self.short_name,
            nodetype='statement',
            is_input=False,
            is_multi=False,
            is_total=False,
            expr=None,
            model=None,
            position=self.G.find_node_position(insert_after),
            insert_after=insert_after,
            hide=None,
        )

    def add_factor(self, name:str, value:typ.Union[np.number, int, float, str, pd.DataFrame, np.ndarray, list]=None):
        if ' ' in name:
            name = self._shorten(name)

        if not self.no_model and isinstance(value, (int, float)):
            self.M.setparam(name) # only Real numbers can be added as params to model
            model = self.M.get(name)
        else:
            model = None

        self.G.add_node(
            name,
            obj=value,
            name=name,
            short_name=name,
            statement=self.short_name,
            nodetype='factor',
            is_input=True,
            is_multi=False,
            is_total=False,
            expr=None,
            model=model,
            position=self.G.find_node_position(None),
            insert_after=None,
            hide=None,
        )

    def add_factors(self, factors:typ.Iterable):
        if isinstance(factors, dict):
            for k,v in factors.items():
                self.add_factor(k, v)
        else:
            for factor in factors:
                self.add_factor(**factor)

    def add_schedule(self, 
        schedule:typ.Union[Schedule, typ.Callable], 
        name:str='',
        short_name:str=None,
        insert_after:str=None,
        **kwargs
        ):
        if callable(schedule):
            schedule = ScheduleFactory(schedule, self)
            schedule.set_call_kwargs(name=name, short_name=short_name, graph=self.graph, **kwargs)
        else:
            schedule.set_graph(self.graph)
    
        self.G.add_node(
            schedule.short_name,
            obj=schedule,
            name=schedule.name, 
            short_name=schedule.short_name,
            statement=self.short_name,
            nodetype='schedule',
            is_input=False,
            is_multi=False,
            is_total=False,
            model=None,
            expr=None,
            position=self.G.find_node_position(insert_after),
            insert_after=insert_after,
            hide=True,
        )

    def add_schedules(self, *schedules:typ.Iterable[Schedule], common_kws={}):
        for sched in schedules:
            self.add_schedule(sched, **common_kws)

    def add_account(
        self, 
        data:typ.Iterable,
        name:str='',
        short_name:str=None,
        periods:pd.PeriodIndex=None,
        index:typ.Iterable=None,
        insert_after:str=None,
        hide:bool=False,
        **kwargs
        ) -> None:
        """
        An lineitem is a pandas object with no predecessors. When an lineitem is added,
        1. it is added as an attribute according to its `short_name`
        2. the Graph is passed into the LineItem
        3. the LineItem is added as a node in the graph

        Parameters:
            data: any python iterables
            name: str
            short_name: str
                used to assign attribute name to the FinancialStatement
            periods: pd.PeriodIndex
                can be passed directly to override class-level attribute
        """
        is_input = True # only time it is not is if it is a function!
        if isinstance(data, (LineItem, MultiLineItem)):
            lineitem = data
            lineitem._graph = self.graph
            if not lineitem.periods.equals(self.periods):
                lineitem.update_periods(self.periods)
        elif isinstance(data, (StatFunction, ScheduleFunction, ScheduleFactory)):
            data.set_call_kwargs(name=name, short_name=short_name, graph=self.graph, **kwargs)
            lineitem = data
            is_input = False
        else:
            if isinstance(data, pd.Series):
                if not name:
                    name = data.name
                data, index = data.values, data.index

            if not name:
                raise ValueError('You must provide `name` attribute if `data` is not type pd.Series')

            data = np.array(data) # To check dimensionality
            periods = periods if periods is not None else self.periods
            if data.ndim == 2:
                lineitem = MultiLineItem(
                    data, 
                    index=index,
                    columns=periods,
                    name=name, 
                    short_name=short_name, 
                    graph=self.graph,
                    **kwargs
                )
            else:
                lineitem = LineItem(
                    data, 
                    index=periods, 
                    name=name, 
                    short_name=short_name, 
                    graph=self.graph,
                    **kwargs
                )

        if lineitem.is_multi:
            self.M.set_multi_index()
        
        if not self.no_model:
            self.M.setparam(lineitem.short_name) # root attribute is a shadow used to generate expressions; must be Var to allow for expressions
            self.M.setparam( f'{lineitem.short_name}_periods', is_multi=lineitem.is_multi) # assign the IndexedParam; this contains actual data and is used in expression transformation
            model = self.M.get(lineitem.short_name)  # the node contains the uninitialized root Var in order to generate epxressions
        else:
            model = 1 # use string so that value can be added/subtracted

        self.G.add_node(
            lineitem.short_name, 
            obj=lineitem,
            name=lineitem.short_name,
            short_name=lineitem.short_name,
            expr=None,
            model=model,
            statement=self.short_name,
            is_input=is_input,
            is_multi=lineitem.is_multi,
            is_total=False,
            nodetype='account',
            position=self.G.find_node_position(insert_after),
            insert_after=insert_after,
            hide=hide
        )
       
    def add_accounts(self, data:typ.Union[pd.DataFrame, LineItem, MultiLineItem, typ.Iterable], *args, common_kws={}) -> None:
        """
        Add multiple accounts with one call.

        If data is a pd.DataFrame, can iterate over the pd.Series rows. Otherwise iterate over the collections.
        """
        if isinstance(data, pd.DataFrame) and not isinstance(data, MultiLineItem):
            for i, row in data.iterrows():
                self.add_account(data=row, **common_kws)
        else:
            if not isinstance(data, (list, tuple, np.ndarray)):
                data = [data]
                if len(args) > 0:
                    data += args

            for account in data:
                if isinstance(account, (LineItem, MultiLineItem)):
                    self.add_account(account, **common_kws)          
                else:
                    self.add_account(**account, **common_kws)

    ### Attached Modules ###
    def add_metrics(self, *args, **kwargs):
        return ModelContextManager(self, *args, **kwargs)

    def valuation(self, *args, **kwargs):
        return Valuation(*args, **kwargs)

    ##### Implementations of common pandas methods #####
    @property
    def iloc(self):
        return self._frame.iloc

    @property
    def loc(self):
        return self._frame.loc

    @property
    def index(self):
        return self._frame.index

    @property
    def shape(self):
        return self._frame.shape

    def resample(self, *args, **kwargs):
        return FinStatResampler(self, *args, **kwargs)

    def groupby(self, *args, **kwargs):
        return FinStatGroupBy(self, *args, **kwargs)

    def reorder_levels(self, *args, **kwargs):
        warnings.warn('`reorder_levels` currently returns a `MultiLineItem` object, NOT a FinancialStatement')
        return self._frame.reorder_levels(*args, **kwargs).sort_index()

    def droplevel(self, *args, **kwargs):
        warnings.warn('`lineitems_only` currently returns a `MultiLineItem` object, NOT a FinancialStatement')
        return self._frame.droplevel(*args, **kwargs)

    def to_csv(self, *args, **kwargs):
        self._frame.to_csv(*args, **kwargs)
