import functools as ft
import warnings
import typing as typ
import numpy as np

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from pandas._typing import TimedeltaConvertibleTypes, TimestampConvertibleTypes
from pandas.core.indexing import _LocIndexer, _iLocIndexer

import networkx as nx   

from ..base import FinStatBaseObject, PERIODS_TO_STRF
from .elements import Elements

def _constructor_wrapper(func, self):
    """
    Takes output from a DataFrameGroupBy method, then 
    reinstantiates the object and passing additional data specific to a
    finstat object 
    """
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(self, *args, **kwargs)
        result = self.obj._constructor(ret.values, index=ret.index, columns=ret.columns, **ret._constructor_kwargs, **kwargs)
        
        return result
    
    return wrapper

class MultiLineGroupBy(DataFrameGroupBy):
    """
    Customized groupby class to control type of the output frame
    """
    def __getattribute__(self, name):
        WRAPPED_FUNCS = ['sum']
        if name in WRAPPED_FUNCS:
            func = super().__getattribute__(name)
            return _constructor_wrapper(func, self)
        else:
            return super().__getattribute__(name)

class MultiLineResampler:
    """
    Customized groupby class to 
    """
    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        self.resampled = obj.to_frame().T.resample(*args, **kwargs)

    def sum(self, *args, **kwargs):
        self._funcstr = 'sum'
        return self._call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        resamp = getattr(self.resampled, self._funcstr)(*args, **kwargs).T
        return self.obj._constructor(resamp.values, index=resamp.index, columns=resamp.columns, **self.obj._constructor_kwargs)

class IndexerMixin:
    def _check_metric(self):
        if self.obj.has_graph:
            nodetype = self.obj.graph.nodes(data='nodetype')[self.obj.short_name]
            if nodetype == 'metric':
                raise Exception('`loc` and `iloc` __setitem__ not available for metric nodetypes')
        else:
            raise Exception('LineItem must have a `_graph` attribute to use `loc`/`iloc` __setitem__')

    def update_model(self, update_key, value):
        self.obj.M._update_param(self.obj.short_name, update_key, value)
        self.obj.solve_out_of_context()

class StatLoc(IndexerMixin, _LocIndexer):
    def __setitem__(self, key, value):
        self._check_metric()

        if isinstance(key, slice):
            index = self.obj.loc[key].index # not circular b/c it uses __getitem__, not __setitem__
            update_key = index.strftime(PERIODS_TO_STRF[index.freqstr])
        else:
            update_key = key

        self.update_model(update_key, value)
   
        super().__setitem__(key, value) # assign updated ONLY AFTER successful model operations to ensure values are not changed

class StatiLoc(IndexerMixin, _iLocIndexer):
    def __setitem__(self, key, value):
        self._check_metric()

        index = self.obj.index[key]
        update_key = index.strftime(PERIODS_TO_STRF[index.freqstr])

        self.update_model(update_key, value)
   
        super().__setitem__(key, value) # assign updated ONLY AFTER successful model operations to ensure values are not changed

class LineItem(FinStatBaseObject, pd.Series):
    """
    A 1-dimensional time-series node in a FinancialStatment graph. Represents a single line item in a 
    financial statement across the given periods.

    The values of an  LineItem can have a "given" object in that its values are provided externally, as opposed to metric
    """
    _metadata = ['_name', '_short_name', '_periods', '_graph']
    _init_keys = ['name', 'short_name', 'graph']

    def __init__(self, values, 
        name:str=None, 
        short_name:str=None, 
        graph:nx.DiGraph=None, 
        **kwargs
    ): 
        super().__init__(values, name=name, **kwargs)

        self._short_name = None
        if short_name:
            self._short_name = short_name
        elif name is not None:
            if not isinstance(name, (pd.Period, tuple)): # when pd.Period or tuple is passed, this is result of _constructor_sliced call from MultiLineItem
                self._short_name = self._shorten(name)

        self._periods = self.index
        self._graph = graph
        self._name = name

    def __hash__(self):
        return hash(self._name)

    @property
    def _constructor(self):
        return LineItem

    @property
    def is_multi(self):
        return False
 
    def update_periods(self, periods:pd.PeriodIndex):
        self.index = periods
        self._periods = periods

    @property
    def loc(self):
        return StatLoc('loc', self)

    @property
    def iloc(self):
        return StatiLoc('iloc', self)

    def to_series(self):
        return pd.Series(self.values, index=self.index, name=self.name)

    def to_multi(self, index:pd.MultiIndex=None):
        """
        Converts the one-level series to a 
        """
        return MultiLineItem(
            self.values.reshape(1,-1), 
            index=index, 
            columns=self.index,
            **self._constructor_kwargs
        )

    def plot(self, *args, **kwargs):
        return self.to_series().plot(*args, **kwargs)

class MultiLineItem(FinStatBaseObject, pd.DataFrame):
    _metadata = LineItem._metadata
    _init_keys = LineItem._init_keys

    @property
    def _constructor(self):
        return MultiLineItem
    
    @property
    def _constructor_sliced(self):
        return LineItem
    
    def __init__(self, 
        values,
        name:str=None, 
        short_name:str=None, 
        graph:nx.DiGraph=None, 
        index:pd.Index=None,
        **kwargs
    ):  
        index = self._clean_index(index, name)
        super().__init__(values, index=index, **kwargs)
    
        self._name = name
        self._short_name = short_name if short_name else (self._shorten(name) if name else None)
        self._graph = graph
        self._periods = self.columns

    def _clean_index(self, index:pd.Index, name:str):
        """
        Attaches 'LineItem' level to index if it does not already exist

        LineItem is only attached if 'LineItem' is not already in the index and
        the object has not been instantiaed through a call to _constructor
        
        The other approach is to override the various methods with _constructor calls to pass a
        flag that prevents the `_reindex` call.
        """
        if index is not None and name is not None:
            if isinstance(index, pd.Index) and index.name == 'Item':
                index = pd.Index([name], name='Item')
            elif 'Item' in index.names:
                index = index.droplevel('Item')

            if not 'Item' in index.names:
                index = self.insert_item_level_in_index(index, name)

        return index

    def multimath(self, item, funcname, **kwargs):
        if isinstance(item, MultiLineItem): # if both terms are MultiLineItem, must insure the indices are aligned
            accounts = Elements(self, item)
            if not accounts.are_aligned:
                left, right = accounts.align()

                return getattr(left, funcname)(right, **kwargs) # passes right back to `multimath` which will now find accounts.are_aligned == True

        result = getattr(super(), funcname)(item)
        return self._constructor(result.values, index=result.index, columns=result.columns, **kwargs)

    def __add__(self, item, **kwargs):
        return self.multimath(item, '__add__', **kwargs)

    def __radd__(self, item, **kwargs):
        return self.multimath(item, '__radd__', **kwargs)

    def __sub__(self, item, **kwargs):
        return self.multimath(item, '__sub__', **kwargs)

    def __rsub__(self, item, **kwargs):
        return self.multimath(item, '__rsub__', **kwargs)

    def __mul__(self, item, **kwargs):
        return self.multimath(item, '__mul__', **kwargs)

    def __rmul__(self, item, **kwargs):
        return self.multimath(item, '__rmul__', **kwargs)

    def __truediv__(self, item, **kwargs):
        return self.multimath(item, '__truediv__', **kwargs)

    def __rtruediv__(self, item, **kwargs):
        return self.multimath(item, '__rtruediv__', **kwargs)

    @property
    def name(self):
        return self._name

    @property
    def is_multi(self):
        return True

    @property
    def has_single_row(self):
        return self.shape[0] == 1

    def update_periods(self, periods:pd.PeriodIndex):
        self.columns = periods
        self._periods = periods

    def insert_item_level_in_index(self, index, name:str=None):
        name = self.name if name is None else name
        frame = index.to_frame().reset_index(drop=True)
        frame.insert(0, 'Item', name)

        return pd.MultiIndex.from_frame(frame)

    def insert_item_level(self, name:str=None):
        """
        Inserts an 'LineItem' level into the index of the LineItem object passed.

        Parameters:
            account: LineItem
        """
        acct = self.copy()
        idx = self.insert_item_level_in_index(acct.index, name)
        acct.index = idx

        return acct

    def categorize_level(self, name, categories):
        idx_frame = self.index_as_frame
        cats = pd.Categorical(idx_frame[name], categories=categories, ordered=True)
        idx_frame.loc[:, name] = cats
        self.index = pd.MultiIndex.from_frame(idx_frame)

    def groupby(
        self,
        by=None,
        axis=0,
        level:None=None,
        *args, **kwargs
        ):
        """Ripped from pandas groupby"""

        if level is None and by is None:
            raise TypeError("You have to supply one of 'by' and 'level'")

        return MultiLineGroupBy(
            obj=self,
            keys=by,
            axis=self._get_axis_number(axis),
            level=level,
            *args, **kwargs
        )

    def resample(self, *args, **kwargs):
        """
        Resample data structure along the columns / periods axis.

        Unlike LineItem objects, MultiLineItem objects must be rotated via `T` then resampled, then rotated back. This is not
        currently supported by MultiLineItem, so the pd.DataFrame is used and the MultiLineItem reconsituted via
        `_constructor`.
        """
        return MultiLineResampler(self, *args, **kwargs)

    # def sum(self, *args, **kwargs):
    #     result = super().sum()
    #     kwargs = result.set_constructor_kwargs(kwargs)
    #     for k, v in kwargs.items(): # `sum` will not pass any _metaparams, so `set_constructor_kwargs` will be full on None that should be replaced
    #         if v is None:
    #             kwargs[k] = self._metaparams[k]

    #     return result._constructor(result.values, index=result.index, **kwargs)

    # def total(self, item=None, **kwargs):
    #     if 'name' not in kwargs or kwargs['name'] is None:
    #         kwargs['name'] = 'Total ' + self.name
    #         kwargs['short_name'] = 'tot_' + self.short_name
        
    #     index_name =  index_values(self.index, kwargs['name'])
    #     index = pd.MultiIndex.from_tuples([index_name], names=self.index.names)
        
    #     total = self.sum().to_multi(index)

    #     return self._constructor(total.values, index=total.index, columns=total.columns, **self.set_constructor_kwargs(kwargs))

    # def cumsum(self, **kwargs):
    #     cumsum = super().cumsum(axis=1)
    #     return self._constructor(cumsum.values, index=cumsum.index, columns=cumsum.columns, **self.set_constructor_kwargs(kwargs))

    # def where(self, func, comp, if_true=None, if_false=None, if_true_neg:bool=False, if_false_neg:bool=False, **kwargs):
    #     if_true = self if if_true is None else if_true
    #     if_false = comp if if_false is None else if_false

    #     if if_true_neg:
    #         if_true = -if_true
    #     if if_false_neg:
    #         if_false = -if_false

    #     result = np.where(func(self, comp), if_true, if_false)

    #     return self._constructor(result, index=self.index, columns=self.columns, **self.set_constructor_kwargs(kwargs))

    # @property
    # def loc(self):
    #     return LineItemLoc('loc', self)

    # @property
    # def iloc(self):
    #     return LineItemiLoc('iloc', self)

    # def update(self, data:typ.Union[dict, list]):
    #     """
    #     Assigns new values to object and cascades updates
    #     to any successor nodes.

    #     Data to update successors is calculated using the Metric keywords stored
    #     in each successor node.
    #     """
    #     if isinstance(data, dict):
    #         for k, v in data.items():
    #             self.loc(push=True, update=True)[k] = v
    #     elif isinstance(data, pd.DataFrame):
    #         if self.index.shape == data.index.shape: # index may be different if schedule is udpated
    #             self.index = data.index
    #             self.loc(push=True, update=True)[:, data.columns] = data.values
    #         else:
    #             self.loc(push=True, update=True)[data.index, data.columns] = data.values
    #     elif isinstance(data, pd.Series):
    #         self.loc(push=True, update=True)[data.index, :] = data
    #     else:
    #         self.iloc(push=True, update=True)[:len(data)] = data

    def to_frame(self, with_periods:bool=True, strftime:str=None):
        frame = super().to_frame()
        if not with_periods and isinstance(frame.columns, pd.PeriodIndex):
            strftime = PERIODS_TO_STRF[frame.columns.freqstr] if strftime is None else strftime
            frame.columns = frame.columns.strftime(strftime)
        return frame

    def to_account(self):
        if self.shape[0] > 1:
            raise ValueError('Only MultiLineItem objects with a single row can be converted to LineItem objects.')
        
        return LineItem(
            self.values[0],  
            index=self.columns,
            **self._metaparams
        )
