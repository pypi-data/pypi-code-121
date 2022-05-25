from notecoin.database.base import meta, engine
from sqlalchemy import Float, BIGINT
from sqlalchemy import Table, Column, String


class BTable:
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


class KlineData(BTable):
    def __init__(self, table_name="kline_data_1min", *args, **kwargs):
        super(KlineData, self).__init__(table_name=table_name, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('source', String(20), comment='source', primary_key=True),
                           Column('symbol', String(30), comment='symbol', primary_key=True),
                           Column('timestamp', BIGINT, comment='timestamp', primary_key=True),
                           Column('open', Float, comment='open', default=0),
                           Column('close', Float, comment='close', default=0),
                           Column('low', Float, comment='low', default=0),
                           Column('high', Float, comment='high', default=0),
                           Column('vol', Float, comment='vol', default=0))
