import warnings
import typing as typ
import numpy as np
import pandas as pd

ElementsType = typ.TypeVar('ElementsType', bound='Elements')

def index_fillers(common_idx):
    fillers = []
    for i, col in common_idx.to_frame().iteritems():
        if pd.api.types.is_period_dtype(col):
            fillers.append(pd.Period('1900-1-1', freq='d'))
        elif pd.api.types.is_numeric_dtype(col):
            fillers.append(0)
        else:
            fillers.append('---')
    return fillers

def index_values(common_idx, placeholder='Other'):
    """
    Creates index values for 'Other' row created for MultiLineItem objects that are created via
    a MetricFunction or concating a set of LineItem objects.

    Index value is '---' or np.nan depending on dtype of the index value.

    Parameters
    -----------
    common_idx: pd.Index
        Index resulting from call to `common_level_values` method of Elements object
    """
    fillers = index_fillers(common_idx)
    row = tuple([placeholder] + fillers[1:]) if len(fillers) > 1 else placeholder

    return row

class Align:
    def __init__(self, items):
        self.items = items
        self.frames = self.items.idx_frames()
    
    def auto_groupby(self):
        shared = self.find_shared_levels()
        rank = self.level_rank(shared)
        match = self.match_rank(rank, self.items)
        return match[match > 0].index.tolist()
    
    def find_shared_levels(self):
        unq, counts = np.unique(np.concatenate(self.items._index_names), return_counts=True)
        return unq[counts == self.items.size]        
    
    def level_rank(self, shared):
        count = pd.Series([], dtype=float)
        for col in shared:
            unqlst = [idx[col].unique() for idx in self.frames]
            unq, counts = np.unique(np.concatenate(unqlst), return_counts=True)
            count.loc[col] = (counts >= self.items.size).sum() / unq.size

        return count.sort_values(ascending=False)    
    
    def match_rank(self, rank, items):
        frames = items.idx_frames()
        match_counts = pd.Series([], dtype='int')
        for i in range(1, rank.index.size):
            shared = rank.index[:-i]
            first, rest = frames[0], frames[1:]
            first = first[shared]

            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning) # catches warning about not inferring number types going forward

                if rest:
                    for nxt in rest:
                        nxt = nxt[shared]
                        first, match_count = self.merge_index_w_indicator(first, nxt)

                    match_counts.loc[shared[-1]] = match_count
    
        return match_counts.iloc[::-1]
    
    def merge_index_w_indicator(self, first, nxt):
        merged = pd.merge(first, nxt, how='outer', indicator=True)
        first = merged[merged._merge == 'both'].drop(columns='_merge')
        match_count = merged._merge.value_counts().both
        return first, match_count
    
    def common_index(self, frames):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning) # catches warning about not inferring number types going forward
        
            first, rest = frames[0], frames[1:]
        
            if rest:
                for nxt in rest:
                    if nxt.shape[0] > 1: # should exclude a total rows
                        first, _ = self.merge_index_w_indicator(first, nxt)

            common = first
            common = pd.MultiIndex.from_frame(common)

        if common.nlevels == 1:
            common = common.get_level_values(0)
            
        return common
    
    def append_uncommon(self, acct, common):
        uncommon = acct.loc[acct.index.difference(common)]
    
        if not uncommon.empty and acct.shape[0] > 1: # should exclude total rows
            other_row = uncommon.sum().rename(index_values(common))
            acct = acct.loc[common].sort_index()
            acct.loc[other_row.name, :] = other_row.values

        return acct
    
    def __call__(self, by=None, with_item=False):
        self.by = by if by else self.auto_groupby()
        
        grouped = self.items.groupby(self.by).drop_item_level()
        common = self.common_index(grouped.idx_frames()) 
        
        aligned = [] 
        for acct in grouped:
            acct = self.append_uncommon(acct, common)
            aligned.append(acct)
        
        items = Elements(*aligned)
        if with_item:
            return items.insert_item_level()
        else:
            return items

class concat:
    """
    Object-based concat method for Elements object. Handles different instances and
    combinations of LineItem objects and MultiLineItem objects.
    """
    def __init__(self, lineitems:ElementsType):
        self.lineitems = lineitems
    
    def _account_only_concat(self):
        concatted = pd.concat(self.lineitems, axis=1).T
        concatted.index.name = 'Item'
        concatted.index = pd.CategoricalIndex(
            concatted.index, 
            categories=self.lineitems.names, 
            ordered=True, 
            name='Item'
        )
        return concatted

    def _multi_level_concat(self, by:typ.Iterable=None, other=True):
        grouped = self.lineitems.align(by, with_item=True)
        concatted = pd.concat(grouped)
        concatted.categorize_level('Item', self.lineitems.names)
        return concatted
    
    def __call__(self, *args, **kwargs):
        if self.lineitems.is_multi.any():
            if self.lineitems.size > 1:
                concatted = self._multi_level_concat(*args, **kwargs) 
            else:
                concatted = self.lineitems[0] # if only 1 lineitem, just return that
        else:
            concatted = self._account_only_concat()

        return concatted

class Elements(np.ndarray):
    """
    Container for LineItem objects. Standard numpy methods and attributes are available.

    Includes several helper methods for manipulating sets of LineItem objects used in 
    MetricFunction and FinancialStatment.

    Issues arise from assigning LineItem objects directly to `obj`, so the str representation is instead.
    The underlying items manipulated are still the LineItem objects, given changes to __getitem__

    Parameters:
        elements: iterable of LineItem objects
    """

    def __new__(cls, *elements):
        obj = np.empty(len(elements), dtype='object').view(cls)
        obj[:] = elements

        for e in obj:
            setattr(obj, e.short_name, e)

        obj.concat = concat(obj)

        return obj
    
    def __array_finalize__(self, obj):
        if obj is None: return
        self.concat = getattr(obj, 'concat', None)

    def __repr__(self):
        joined = ', '.join(self.names)
        return f'Elements([{joined}])'

    def __add__(self, elements):
        return Elements(*[acct for acct in self] + [acct for acct in elements])

    @property
    def _index_names(self):
        return [np.array(acct.index.names) for acct in self]

    @property
    def names(self):
        return np.array([e.name for e in self])

    @property
    def short_names(self):
        return np.array([e.short_name for e in self])

    @property
    def is_multi(self):
        return np.array([e.is_multi for e in self])

    @property
    def any_multi(self):
        return np.any(self.is_multi)

    @property
    def are_aligned(self):
        return all([self[0].index.equals(e.index) for e in self[1:]])

    @property
    def have_single_row(self):
        return np.array([e.has_single_row for e in self])

    def update_graphs(self, graph):
        [e.update_graph(graph) for e in self]

    def idx_frames(self):
        return [e.index.to_frame().reset_index(drop=True).apply(lambda col: col.astype(object)) for e in self]

    def groupby(self, by):
        return Elements(*[e.groupby(by).sum() for e in self])

    def strf_columns(self):
        from ..base import PERIODS_TO_STRF
        items = []
        for item in self:
            item.columns = item.columns.strftime(PERIODS_TO_STRF[item.columns.freqstr]).tolist()
            items.append(item)
        return Elements(*items)

    def to_multi(self):
        return Elements(*[e.to_multi() if not is_multi else e for is_multi, e in zip(self.is_multi, self)])

    def to_elements(self):
        return Elements(*[e.to_account() if single else e for single, e in zip(self.have_single_row, self)])

    def drop_item_level(self):
        return Elements(*[e.droplevel('Item') if 'Item' in e.index.names else e for e in self])

    def insert_item_level(self):    
        return Elements(*[e.insert_item_level() for e in self])
    
    def by_position(self):
       return Elements(*sorted(self, key=lambda n: n.graph.nodes[n.short_name]['position']))

    @property
    def align(self):
        return Align(self)
        