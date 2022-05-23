from jdw.kdutils.singleton import Singleton
from ..operator_engine import OperatorEngine
from jdw.mfc.experimental import ATL_URL
import pandas as pd
import os,six,pdb


@six.add_metaclass(Singleton)
class FetchATLEngine(OperatorEngine):
    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(FetchATLEngine, self).__init__('ATL', ATL_URL)
        else:
            super(FetchATLEngine, self).__init__(name, uri)

    def account(self, table_name, account_id, password, plt, columns):
        query = {'account_id':account_id, 'password':password, 'plt':plt}
        result = self.fetch(table_name=table_name,query=query,columns=columns)
        result = pd.DataFrame(result)
        result = self._filter_columns(result) if not result.empty else result
        result = result.to_dict(orient='records')[0] if not result.empty else {}
        return result

@six.add_metaclass(Singleton)
class InsertATLEngine(OperatorEngine):
    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(InsertATLEngine, self).__init__('ATL', ATL_URL)
        else:
            super(InsertATLEngine, self).__init__(name, uri)

    def account(self, table_name, data):
        columns = ['account_id','password','plt']
        self.insert(table_name=table_name, data=data, columns=columns)

@six.add_metaclass(Singleton)
class ATLEngine(InsertATLEngine, FetchATLEngine):
    def account(self, table_name, **kwargs):
        if kwargs['method'] == 'insert':
            return InsertATLEngine.account(self, table_name=table_name, data=kwargs['data'])
        elif kwargs['method'] == 'fetch':
            columns = kwargs['columns'] if 'columns' in kwargs else None
            return FetchATLEngine.account(self, table_name=table_name,
                    account_id=kwargs['account_id'], password=kwargs['password'],
                    plt=kwargs['plt'], columns=columns)