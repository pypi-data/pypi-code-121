# -*- coding: utf-8 -*-
import six,datetime,pdb,importlib
import pandas as pd
from sqlalchemy import create_engine, select, and_
from sqlalchemy.ext.automap import automap_base
import sqlalchemy.orm as orm
from kdutils.singleton import Singleton

#@six.add_metaclass(Singleton)
class SQLEngine(object):
    def __init__(self, url):
        self._engine = create_engine(url, echo=False)
        self._session = self.create_session()
        
    def create_session(self):
        db_session = orm.sessionmaker(bind=self._engine)
        return db_session()

    def __del__(self):
        if self._session:
            self._session.close()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.close()

    def sql_engine(self):
        return self._engine
    

class FetchEngine(object):
    def __init__(self, name, url):
        self._name = name
        self._engine = SQLEngine(url)
        self._base = automap_base()
        self._base.prepare(self._engine.sql_engine(), reflect=True)
        
    @classmethod
    def create_engine(cls, name):
        if name == 'dx':
            return importlib.import_module('data.db.dx.dx_engine').__getattribute__('FetchDXEngine')
        elif name == 'kd':
            return importlib.import_module('data.db.kd.kd_engine').__getattribute__('FetchKDEngine')
        elif name == 'rl':
            return importlib.import_module('data.db.rl.rl_engine').__getattribute__('FetchRLEngine')
        
    def base_fuzzy(self, table, key, words, columns=None):
        cols = []
        if columns is not None:
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        rule = and_(*[table.__dict__[key].like('%' + w + '%') for w in words])
        query = select(cols).where(rule)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result
        
    def base_notime(self, table, codes=None, key=None, columns=None, freq=None,  clause_list=None):
        if codes is not None:
            condition = and_(table.__dict__[key].in_(codes)) if clause_list is None else clause_list
        elif codes is None and clause_list is not None:
            condition = clause_list
        cols = []
        if columns is not None:
            if codes is not None:
                cols.append(table.__dict__[key])
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        query = select(cols).where(condition) if key is not None else select(cols)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result
    
        
    def base_bytime(self, table, begin_date, end_date, codes, key=None, date_key='trade_date', 
                    columns=None, freq=None, dates=None, clause_list=None):
        if dates is not None:
            condition = and_(table.trade_date.in_(dates), table.__dict__[key].in_(codes)
                            ) if clause_list is None else clause_list
        elif codes is not None:
            condition = and_(table.__dict__[date_key] >= begin_date, table.__dict__[date_key] <= end_date,
                         table.__dict__[key].in_(codes)) if clause_list is None else clause_list
        elif clause_list is not None:
            condition = clause_list
        else:
             condition = and_(table.__dict__[date_key] >= begin_date, 
                              table.__dict__[date_key] <= end_date)
            
        cols = [table.__dict__[date_key]]
        if columns is not None:
            if key is not None:
                cols.append(table.__dict__[key])
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        query = select(cols).where(condition).order_by(table.__dict__[date_key].desc())
        result = pd.read_sql(query, self._engine.sql_engine())
        return result
    
    def base(self, table, begin_date, end_date, codes, time_name='trade_date',
             key=None, columns=None, 
             freq=None, dates=None, clause_list=None):
        if dates is not None:
            condition = and_(table.trade_date.in_(dates), table.__dict__[key].in_(codes)
                            ) if clause_list is None else clause_list
        else:
            condition = and_(table.trade_date >= begin_date, table.trade_date <= end_date,
                         table.__dict__[key].in_(codes)) if clause_list is None else clause_list
        cols = [table.__dict__[time_name]]
        if key is not None:
            cols.append(table.__dict__[key])
        if columns is not None:
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        if dates is not None:
            query = select(cols).where(condition)
        else:
            query = select(cols).where(condition)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result