import pdb,os
from pymongo import InsertOne,DeleteOne
from pymongo.errors import BulkWriteError
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


class OperatorEngine(object):
    def __init__(self, name, uri):
        self._name = name
        self._engine = MGEngine(uri)

    @classmethod
    def create_engine(cls, name):
        if name == 'ntn':
            from .ntn import engine
            return engine.__getattribute__('NTNEngine')
        elif name == 'atl':
            from .atl import engine
            return engine.__getattribute__('ATLEngine')

    def _filter_columns(self, result):
        if not result.empty:
            result =  result.drop(['_id'],axis=1) if '_id' in result.columns else result
            result =  result.drop(['flag'],axis=1) if 'flag' in result.columns else result
            result =  result.drop(['timestamp'],axis=1) if 'timestamp' in result.columns else result
        return result
        
    def fetch(self, table_name, query, columns=None):
        cols = columns if columns is None else dict(zip(
            columns, [1 for i in range(0, len(columns))]))
        return self._engine.mg_engine()[self._engine.mg_collection()][table_name].find(query, cols)
    
    def insert(self, table_name, data, columns):
        insert_request = [InsertOne(d) for d in data.to_dict(orient='records')]
        delete_request = [DeleteOne(d) for d in data[columns].to_dict(orient='records')]
        _ = self._engine.mg_engine()[self._engine.mg_collection()][table_name].bulk_write(
            delete_request, bypass_document_validation=True)
        _ = self._engine.mg_engine()[self._engine.mg_collection()][table_name].bulk_write(
            insert_request, bypass_document_validation=True)
    def automap(self, table_name):
        return [col for col in self._engine.mg_engine(
            )[self._engine.mg_collection()][table_name].find_one().keys() if col not in ['timestamp','flag','_id','trade_date','code']]