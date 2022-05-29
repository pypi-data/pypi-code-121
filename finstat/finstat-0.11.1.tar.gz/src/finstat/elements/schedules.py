import warnings
import typing as typ
import inspect
import functools as ft
import numpy as np
import pandas as pd

import networkx as nx

from ..base import FinStatBaseObject
from ..functions.base import FuncMixin
from .lineitem import MultiLineItem

ScheduleType = typ.TypeVar('ScheduleType', bound='Schedule')

# Helpers map list of value and date items to a schedule containing
# all dates in a given set of periods
def _create_arr(values:np.ndarray, periods:pd.PeriodIndex) ->  np.ndarray:
    """
    Creates m x n array, where m is df.shape[0], or the number of values to be mapped, and n is len(periods), or the number of dates
    available on which values can be mapped. Each row in the array contains only one value in the index == 0 location of that row.
    
    Parameters:
        values: pandas Series or numpy n x 1 ndarray
        periods: pandas PeriodIndex
            
    Return:
        arr: (m x n) numpy ndarray
            m == len(values), or the number of items to be mapped and n == len(periods), or the number of periods considered.
            arr contains one value per row, all in the index 0 location of that row.
    """
    arr = np.zeros((len(values), periods.size))
    arr[:, 0] = values
    
    return arr

def relocate(arr:np.ndarray, locs:np.ndarray, direction:str='forward') -> np.ndarray:
    """
    Intermediate helper that shifts each index 0 location value in `arr` to the location found in `locs`.
    
    Numba could be used to improve speed for large `arr`.
    
    `ogrid` is used to produce arrays of row and column indices. The locations are then subtracted from the
    column indices. `arr` is then resorted with update column indices. This results in the values at index 0 
    moving to the index location specified in `locs`. 

    Parameters:
        values: pandas Series or numpy n x 1 ndarray
        periods: pandas PeriodIndex
            
    Return:
        arr: (m x n) numpy ndarray
            m == len(values), or the number of items to be mapped and n == len(periods), or the number of periods considered.
            arr contains one value per row, each value positioned in the index location specified by `locs`.

    """
    rows, column_indices = np.ogrid[:arr.shape[0], :arr.shape[1]]
    if direction == 'forward':
        column_indices = column_indices - locs[:, np.newaxis]
    elif direction == 'backward':
         column_indices = column_indices + locs[:, np.newaxis]
    return arr[rows, column_indices]

def map_to_periods(values:np.ndarray, dates:np.ndarray, periods:pd.PeriodIndex) -> np.ndarray:
    """
    Process:
        1. Create m x n array for each m item in df to be mapped and n periods on which the values are to be mapped
        2. 
    
    Parameters:
        values: n x 1 np.ndarray
        dates: n x 1 np.ndarray of datetime-like objects
        periods: pandas PeriodIndex

    Return:
        arr: (m x n) numpy ndarray
            m == len(values), or the number of items to be mapped and n == len(periods), or the number of periods considered.
            arr contains one value per row, each value positioned in the index location specified by `locs`.
    """
    arr = _create_arr(values, periods)
    locs = periods.searchsorted(dates)
    arr = relocate(arr, locs)
    
    return arr

class ScheduleFactory(FuncMixin):
    def __init__(self, func:typ.Callable, finstat:'FinancialStatement'=None, **kwargs):
        self.EXPECTED_FACTORS = inspect.getfullargspec(func).annotations
        self.schedfunc = func
        self.factors = {}
        self.finstat = finstat
        self.fkwargs = kwargs

    def set_factors(self):
        if self.finstat is not None:
            for factor in self.EXPECTED_FACTORS:
                self.factors[factor] = getattr(self.finstat, factor)
        else:
            for k, v in self.fkwargs.items():
                if k in self.EXPECTED_FACTORS:
                    self.factors[k] = v # when another schedule is passed don't make it a factor

    def __call__(self, *args, **kwargs):
        self.set_factors()
        sched = self.schedfunc(**self.factors)
        sched = Schedule(sched, *args, factory=self, **kwargs, **self.call_kwargs)
        if self.finstat is not None:
            sched.set_graph(self.finstat.graph)

        return sched

class ScheduleFunction(FuncMixin):
    def __init__(self, sched, func, *args, **kwargs):
        ft.update_wrapper(self, func)
        self.sched = sched
        self.func = func
        self.fargs = args
        
        self._periods = kwargs.pop('periods', None)
        self.fkwargs = kwargs

    @property
    def periods(self):
        if hasattr(self, '_periods') and self._periods is not None:
            return self._periods
        else:
            if self.sched.has_graph:
                return self.graph.graph['periods']
            else:
                raise ValueError('You must provide `periods` argument if the schedule is not part of a FinancialStatement')

    @property
    def index(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            return pd.MultiIndex.from_frame(self.sched)

    @property
    def is_multi(self):
        return True # allows ScheduleFunction to act as a MultiLineItem in `add_account` method

    def col_values(self, sched, col:str):
        return sched[col].values

    def __call__(self, *args, **kwargs):
        sched = self.sched._factory() if self.sched.has_factory else self.sched
        fargs = [self.col_values(sched, col) for col in self.fargs]
        fkwargs = {k: self.col_values(sched, col) for k, col in self.fkwargs.items()}
        obj = self.func(*fargs, periods=self.periods, **fkwargs)

        return MultiLineItem(
            obj,
            columns=self.periods,
            index=pd.MultiIndex.from_frame(sched),
            *args,
            **kwargs,
            **self.call_kwargs
        )

class Schedule(FinStatBaseObject, pd.DataFrame):
    """
    Container and handler class for a list of invoice or purchase orders.
    """
    _metadata = ['_name', '_short_name', '_graph', '_sched_maker']

    def __init__(self, 
        *args, 
        name:str=None, 
        short_name:str=None, 
        graph:nx.DiGraph=None,
        factory:typ.Callable=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._graph = graph
        self._name = name
        self._short_name = short_name if short_name else self._shorten(name)
        self._factory = factory

    @property
    def _constructor(self):
        return Schedule

    @property
    def name(self):
        return self._name

    @property
    def sched_maker(self):
        return self._sched_maker

    @property
    def has_factory(self):
        return self._factory is not None

    def set_factory(self, factory):
        self._factory = factory

    def map_schedule(self,
        value_column:str=None,
        date_column:str=None,
        periods:pd.PeriodIndex=None,
        return_sched:bool=False
        ):
        funcobj = ScheduleFunction(self, map_to_periods, value_column, date_column, periods=periods)

        if self.has_graph and not return_sched:
            return funcobj
        else:
            return funcobj()
