from sqlalchemy import BIGINT, Column, Float, String, Table

from .base import BaseTable, meta


class KlineData(BaseTable):
    def __init__(self, table_name="kline_data_1min", *args, **kwargs):
        super(KlineData, self).__init__(table_name=table_name, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('symbol', String(30), comment='symbol', primary_key=True),
                           Column('timestamp', BIGINT, comment='timestamp', primary_key=True),
                           Column('open', Float, comment='open', default=0),
                           Column('close', Float, comment='close', default=0),
                           Column('low', Float, comment='low', default=0),
                           Column('high', Float, comment='high', default=0),
                           Column('vol', Float, comment='vol', default=0))
