import pdb
from jdw.kdutils.data.mongodb import MongoDBManager
from jdw.kdutils.logger import kd_logger

class MGEngine(object):
    def __init__(self, uri):
        self._engine = MongoDBManager(uri=uri)
        self._collection = uri.split('/')[-1]
    #def __del__(self):
    #    conn.dispose()
        
    def mg_engine(self):
        return self._engine
    
    def mg_collection(self):
        return self._collection


class FetchEngine(object):
    def __init__(self, name, uri):
        self._name = name
        self._engine = MGEngine(uri)

    @classmethod
    def create_engine(cls, name):
        if name == 'kn':
            from .kn import kn_engine
            return kn_engine.__getattribute__('FetchKNEngine')

    def base(self, table_name, query, columns=None):
        cols = columns if columns is None else dict(zip(
            columns, [1 for i in range(0, len(columns))]))
        return self._engine.mg_engine()[self._engine.mg_collection()][table_name].find(query, cols)
    
    def automap(self, table_name):
        return [col for col in self._engine.mg_engine(
            )[self._engine.mg_collection()][table_name].find_one().keys() if col not in ['timestamp','flag','_id','trade_date','code']]