from jdw.kdutils.singleton import Singleton
from ..operator_engine import OperatorEngine
from jdw.mfc.experimental import NTN_URL
import pandas as pd
import os,six,pdb



@six.add_metaclass(Singleton)
class FetchNTNEngine(OperatorEngine):
    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(FetchNTNEngine, self).__init__('NTN', NTN_URL)
        else:
            super(FetchNTNEngine, self).__init__(name, uri)

    def _general_query(self, **kwargs):
        query = {}
        if 'begin_date' in kwargs and 'end_date' in kwargs:
            query['trade_date'] = {"$gte": kwargs['begin_date'],
                                   "$lte": kwargs['end_date']
            }
        if 'codes' in kwargs:
            query['code'] = {'$in':kwargs['codes']}
        return query
    
    def research(self, table_name, codes, begin_date, end_date, columns=None):
        query = {}
        query['trade_date'] = {"$gte": begin_date,
                                "$lte": end_date}
        query['code'] = {'$in':codes}
        if columns is not None:
            query['name'] = {'$in':columns}
        result = self.fetch(table_name=table_name,query=query,columns=None)
        result = pd.DataFrame(result)
        result = self._filter_columns(result)
        if not result.empty:
            result = result.set_index(
                ['trade_date','code','name'])['value'].unstack().reset_index()
            result.columns.name=''
        return result


@six.add_metaclass(Singleton)
class InsertNTNEngine(OperatorEngine):
    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(InsertNTNEngine, self).__init__('NTN',NTN_URL)
        else:
            super(InsertNTNEngine, self).__init__(name, uri)

    def research(self, table_name, data):
        columns = ['trade_date','code','name']
        data = data.set_index(['trade_date','code']).stack().reset_index()
        data.rename(columns={'level_2':'name',0:'value'},inplace=True)
        data['trade_date'] = pd.to_datetime(data['trade_date']).dt.strftime('%Y-%m-%d')
        self.insert(table_name=table_name, data=data, columns=columns)


@six.add_metaclass(Singleton)
class NTNEngine(InsertNTNEngine,FetchNTNEngine):
    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(NTNEngine, self).__init__('NTN',NTN_URL)
        else:
            super(NTNEngine, self).__init__(name, uri)

    def research(self, table_name, **kwargs):
        if kwargs['method'] == 'insert':
            return InsertNTNEngine.research(self, table_name=table_name, data=kwargs['data'])
        elif kwargs['method'] == 'fetch':
            columns = kwargs['columns'] if 'columns' in kwargs else None
            return FetchNTNEngine.research(self, table_name=table_name, 
                    codes=kwargs['codes'], begin_date=kwargs['begin_date'], 
                    end_date=kwargs['end_date'], columns=columns)