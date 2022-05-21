from tardis.clients.csv_client import ExchangeCSVClient
from tardis.database.client import ConstanceDBClient
from tardis.database.table import ConstanceDBTable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
import pandas as pd


class BaseTardisIngestor(ABC):
    def __init__(
        self,
        exchange: str,
        period_seconds: int,
        db_credentials: dict,
        tardis_api_key: str,
    ):
        self.tardis_client = ExchangeCSVClient(exchange, tardis_api_key)
        self.period = timedelta(seconds=period_seconds)
        self.db_client = ConstanceDBClient(**db_credentials)
        self.table = self._get_table(exchange, self.period)
        self.symbol = self._get_symbol()

    @abstractmethod
    def _get_table(self, exchange: str, period: timedelta) -> ConstanceDBTable:
        pass

    @abstractmethod
    def _get_symbol(self) -> str:
        pass

    @abstractmethod
    def _get_data(
        self, max_days: int, first_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        pass

    @abstractmethod
    def _get_time_cols(self) -> List[str]:
        pass

    def _insert_data(self, data: pd.DataFrame, time_cols: List[str]):
        self.table.insert_data(data, time_cols=time_cols)

    def _get_symbol_datetime_range(self) -> Tuple[datetime, datetime]:
        range_start, range_end = self.tardis_client.get_symbol_date_range(self.symbol)
        range_start = datetime(range_start.year, range_start.month, range_start.day)
        range_end = datetime(range_end.year, range_end.month, range_end.day)
        return range_start, range_end

    def _get_sync_range(self, max_days: int) -> Tuple[datetime, datetime]:
        range_start, range_end = self._get_symbol_datetime_range()
        latest_time = self.table.get_latest_time()

        sync_start = latest_time + self.period if latest_time else range_start
        sync_end = min(sync_start + timedelta(days=max_days), range_end)
        return sync_start, sync_end

    def sync(self, max_days: int, first_date: str = None):
        if isinstance(first_date, str):
            first_date = datetime.strptime(first_date, "%Y-%m-%d")
        time_cols = self._get_time_cols()
        new_data = self._get_data(max_days, first_date)
        if new_data is not None and len(new_data) > 0:
            print(f"Inserting {len(new_data)} rows with columns {new_data.columns}")
            self._insert_data(new_data, time_cols=time_cols)
