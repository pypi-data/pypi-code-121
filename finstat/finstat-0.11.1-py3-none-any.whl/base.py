import numpy as np
import pandas as pd

MATH_METHODS = ['__add__', '__sub__', '__mul__', '__truediv__', '__radd__', '__rsub__', '__rmul__', '__rtruediv__']

### Helpers for converting between pandas period objects and strings ###
PANDAS_FREQ_OFFSET = [
    '10T', 'D', 'B', 'C', 'W', 'SM', 'SMS', 'M', 'BM' , 'CBM', 'MS', 'BMS', 'CBMS', 'Q', 'BQ',
    'QS', 'BQS', 'A', 'Y', 'BA', 'BY', 'AS', 'YS', 'BAS', 'BYS'
]
FREQ_MAP = {freqstr: v for freqstr, v in zip(PANDAS_FREQ_OFFSET, np.arange(len(PANDAS_FREQ_OFFSET)))}
PERIODS_TO_STRF = {
    '10T': '%d-%m-%y %H:%M', 
    'D': '%d-%m-%y',
    'W': '%d-%m-%y',
    'W-SUN': '%d-%b-%y',
    'M': '%Y-%m',
    'Q': '%b-%Y',
    'Q-DEC': '%b-%Y',
    'A-DEC': '%Y',
    'A': '%Y',
}

class GraphNotAssignedError(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        if msg is None:
            msg = 'Object has not been assigned to a statement and so does not have a graph.'
        super().__init__(msg, *args, **kwargs)

class FinStatBaseObject:
    @property
    def _metaparams(self):
        """
        Used to pass metadata as kwargs on _constructor calls.

        Used in _constructor_wrapper
        """
        return {meta.lstrip('_'): getattr(self, meta) for meta in self._metadata}

    @property
    def _metaattrs(self):
        """
        Used to pass metadata as kwargs to `_update_meta` calls
        """
        return {meta: getattr(self, meta) for meta in self._metadata}

    @property
    def _constructor_kwargs(self):
        return {k: getattr(self, k) for k in self._init_keys}

    def _filter_constructor_kwargs(self, kwargs):
        for k, v in self._constructor_kwargs.items():
            if k not in kwargs:
                kwargs[k] = v

        return kwargs

    @property
    def short_name(self):
        return self._short_name

    @property
    def periods(self):
        return self._periods

    @property
    def graph(self):
        return self._graph

    @property
    def G(self):
        return self._graph

    @property
    def has_graph(self):
        return self.graph is not None

    def set_graph(self, graph):
        self._graph = graph

    def update_graph(self, graph):
        from .statement import StatGraph
        super().__setattr__('_graph', StatGraph(self, graph))

    def has_node(self, name):
        return self.has_graph and name in self._graph.nodes

    @property
    def AS_EXPR(self):
        return self.has_graph and self.graph.graph['OPEN_MODEL_CONTEXT']

    def open_model_context(self):
        if self.has_graph:
            self.graph.graph['OPEN_MODEL_CONTEXT'] = True
        else:
            raise GraphNotAssignedError

    def close_model_context(self):
        if self.has_graph:
            self.graph.graph['OPEN_MODEL_CONTEXT'] = False
        else:
            raise GraphNotAssignedError

    @property
    def model_context_is_open(self):
        return self.graph.graph['OPEN_MODEL_CONTEXT']

    @property
    def M(self):
        return self._graph.graph['model_mngr']

    def solve_out_of_context(self):
        self.open_model_context()
        self.M.solve()
        self.close_model_context()

    @property
    def successors(self):
        if self.has_graph:
            return list(self.graph.successors(self.short_name))
        else:
            raise GraphNotAssignedError

    @property
    def is_multi(self):
        NotImplementedError

    @property
    def index_as_frame(self):
        return self.index.to_frame().reset_index(drop=True)

    def _shorten(self, name, short_name=None) -> str:
        """"
        Logic for creating shorthand name for an LineItem object
        
        Examples:
            'Revenue' -> 'revenue'
            'Cost of Goods Sold' -> 'cogs'
            'Amortization' -> 'amort'

        Parameters:
            name: str
        """ 
        if short_name is None:
            if isinstance(name, (int, float)):
                return str(name)
            if name in ['', None]:
                return name
            elif name == 'Income Statement':
                return 'istat'
            elif len(name.split(' ')) > 1:
                return ''.join(s[0].lower() for s in name.split(' '))
            elif len(name) > 10:
                return name[:5].lower()
            else:       
                return name.lower()
        else:
            return short_name

    def to_frame(self):
        return pd.DataFrame(self.values, index=self.index, columns=self.columns)

    def compare_freq(self, freq_a:str, freq_b:str):
        freq_a = freq_a.split('-')[0]
        freq_a = ''.join([i for i in freq_a if not i.isdigit()])
        freq_b = freq_b.split('-')[0]
        freq_b = ''.join([i for i in freq_b if not i.isdigit()])
        return FREQ_MAP[freq_a] > FREQ_MAP[freq_b]
