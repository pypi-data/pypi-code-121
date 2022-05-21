from datetime import datetime
from typing import List, Optional
import pandas as pd
from sqlalchemy.engine import Engine


class ConstanceDBTable:
    TIME_COL = "timestamp"

    def __init__(self, engine: Engine, name: str):
        self._engine = engine
        self.name = name

    def get_latest_time(self) -> Optional[datetime]:
        result = pd.read_sql(
            f"SELECT {self.TIME_COL} FROM {self.name} ORDER BY {self.TIME_COL} DESC LIMIT 1",
            self._engine,
        )
        if len(result) > 0:
            return result.iloc[0, 0]

    def get_snapshot(self, timestamp: datetime) -> pd.DataFrame:
        return pd.read_sql(
            f"SELECT * FROM {self.name} WHERE {self.TIME_COL} = '{timestamp}'",
            self._engine,
        )

    def insert_data(self, data: pd.DataFrame, time_cols: Optional[List[str]] = None):
        data = data.dropna(axis=1)
        for time_col in time_cols:
            if time_col in data.columns:
                if data[time_col].dtype != "datetime64[ns]":
                    data.loc[:, time_col] = pd.to_datetime(data[time_col], unit="us")
        print(f"Inserting {len(data)} rows to {self.name} with columns {data.columns}")
        data.to_sql(
            self.name,
            self._engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )
