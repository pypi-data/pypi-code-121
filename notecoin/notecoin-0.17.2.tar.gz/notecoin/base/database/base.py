import logging
import os

from notetool.secret import read_secret
from sqlalchemy import (BIGINT, Column, Float, MetaData, String, Table,
                        create_engine)
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
        self.table: Table
        meta.create_all(engine)

    def insert(self, values, *args, **kwargs):
        meta.create_all(engine)
        cols = [col.name for col in self.table.columns]
        if isinstance(values, dict):
            values = dict([(k, v) for k, v in values.items() if k in cols])
        elif isinstance(values, list):
            values = [dict([(k, v) for k, v in item.items() if k in cols]) for item in values]
        ins = self.table.insert(values=values).prefix_with("OR REPLACE")
        engine.execute(ins)
