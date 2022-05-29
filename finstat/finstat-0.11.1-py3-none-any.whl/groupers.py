from .optimize import ModelManager

ScheduleFunction = None
########### Since financial statements are built from income statement to balance sheet, never nee dalst, only need `sum`


### WHEN RESAMPLE ###
# 1. Underlying DiGraph is copied to the new global statement constructor
# 2. This carries over all elements from the original statement
# 3. All elements containing a DiGraph MUST have their DiGraphs updated
# 4. The original instantiated ModelManager, however, is carried across in the copied DiGraph
# 5. After instantiation, the ModelManager must be overwritten, this time with the new grouped statement and a clone of the origina AbstractModel
# 5. So, ALL elements have a new DiGraph, which is the same among all the elements
# 6. And ALL elements have a new ModelManager and new underlying AbstractModel, which is a clone of the original
# 7. this should allow parameters to be updated via `instance_data` and new instances to be created without issue
class Grouper:
    def __init__(self, stat, *args, **kwargs):
        self.grouped = stat._constructor(name=stat.name, short_name=stat.short_name, graph=stat.G._graph.copy(), *args, **kwargs)
        for substat in stat.statements:
            self.grouped.add_statement(name=substat.name, short_name=substat.short_name) # have to create new substatement nodes
        self.grouped.G.graph['model_mngr'] = ModelManager(self.grouped, self.grouped.G.graph['model_mngr'].abstract.clone())
        self.grouped.elements.update_graphs(self.grouped.graph._graph)
        self.grouped.M.update_stat(self.grouped)
    
    def sum(self, *args, **kwargs):
        self.funcstr = 'sum'
        return self._call(*args, **kwargs)

    def last(self, *args, **kwargs):
        self.funcstr = 'sum'
        return self._call(*args, **kwargs)

    def mean(self, *args, **kwargs):
        self.funcstr = 'mean'
        return self._call(*args, **kwargs)

class FinStatResampler(Grouper):
    def __init__(self, stat, freq='A-DEC'):
        super().__init__(stat)
        self.freqstr = freq

        _new_periods = stat.periods.asfreq(self.freqstr).unique()
        self.grouped.update_periods(_new_periods)

    def resamp_accounts(self, *args, **kwargs):
        last = kwargs.pop('last', [])
        mean = kwargs.pop('mean', [])
        summ = kwargs.pop('summ', []) 
        
        for name, obj in self.grouped.G.filter_nodes_by_attribute('nodetype', 'account', data='obj', return_tuple=True):
            resampled = obj.resample(self.freqstr)
            if name in last:
                funcstr = 'last'
            elif name in mean:
                funcstr = 'mean'
            elif name in summ:
                funcstr = 'sum'
            else:
                funcstr = self.funcstr
            self.grouped.G.nodes[name]['obj'] = getattr(resampled, funcstr)(*args, **kwargs)

    def _call(self, *args, last=[], **kwargs):
        self.resamp_accounts(*args, last=last, **kwargs)
        
        if hasattr(self.grouped.M.abstract, 'obj'):
            self.grouped.M.create_instance()
            self.grouped.solve_out_of_context()
        
        return self.grouped

class FinStatGroupBy(Grouper):
    def __init__(self, stat, by):
        super().__init__(stat)
        self.grouped.G.graph['by'] = by

    def _call(self, *args, **kwargs):
        self.grouped.M.create_instance()
        self.grouped.solve_out_of_context()
        return self.grouped
