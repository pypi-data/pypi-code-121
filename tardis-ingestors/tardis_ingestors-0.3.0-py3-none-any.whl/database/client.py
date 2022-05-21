import sqlalchemy
from datetime import timedelta
from tardis.database.table import ConstanceDBTable


class ConstanceDBClient:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.engine = sqlalchemy.create_engine(
            f"postgresql+pg8000://{user}:{password}@{host}:{port}/{database}"
        )

    def _period_to_string(self, period: timedelta) -> str:
        if period >= timedelta(days=1):
            return f"{period.days}d"
        elif period >= timedelta(hours=1):
            return f"{period.seconds // 3600}h"
        elif period >= timedelta(minutes=1):
            return f"{period.seconds // 60}m"
        else:
            return f"{period.seconds}s"

    def get_table(self, type: str, period: timedelta, source: str) -> ConstanceDBTable:
        table_name = f"{type}_{self._period_to_string(period)}_{source}"
        # sqlalchemy.inspect(self.engine).has_table(table_name)
        return ConstanceDBTable(self.engine, table_name)
