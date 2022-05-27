import logging
import os

from notetool.secret import read_secret
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import declarative_base

uri = read_secret(cate1='notecoin', cate2='dataset', cate3='db_path')
uri = uri or f'sqlite:///{os.path.abspath(os.path.dirname(__file__))}/data/notecoin.db'
# engine = create_engine(uri, echo=True)
meta = MetaData()
engine = create_engine(uri)
Base = declarative_base()
logging.info(f'uri:{uri}')


class BaseTable:
    def __init__(self, table_name, *args, **kwargs):
        self.table_name = table_name
        self.table: Table = None
        meta.create_all(engine)

    def insert(self, values, keys=None, *args, **kwargs):
        meta.create_all(engine)
        cols = [col.name for col in self.table.columns]
        if isinstance(values, dict):
            values = dict([(k, v) for k, v in values.items() if k in cols])
        elif isinstance(values, list):
            if isinstance(values[0], dict):
                values = [dict([(k, v) for k, v in item.items() if k in cols]) for item in values]
            elif isinstance(values[0], list):
                values = [dict(zip(keys, item)) for item in values]
        insert_stmt = insert(self.table).values(values)
        self.on_duplicate_key_update(insert_stmt)

    def on_duplicate_key_update(self, insert_stmt):
        return engine.execute(insert_stmt.on_duplicate_key_update(symbol=insert_stmt.inserted.symbol))
