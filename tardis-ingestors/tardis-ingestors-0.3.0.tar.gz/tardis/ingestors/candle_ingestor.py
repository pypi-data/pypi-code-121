from typing import Optional, List
from tardis.ingestors.base_ingestor import BaseTardisIngestor
from tardis.database.table import ConstanceDBTable
import pandas as pd
from datetime import timedelta


class CandleTardisIngestor(BaseTardisIngestor):
    SYMBOL = "SPOT"
    TABLE_TYPE = "ohlcv"

    def _get_table(self, exchange: str, period: timedelta) -> ConstanceDBTable:
        return self.db_client.get_table(self.TABLE_TYPE, period, exchange)

    def _get_symbol(self) -> str:
        return self.SYMBOL

    def _get_time_cols(self) -> List[str]:
        return ["timestamp"]

    def _get_data(self, max_days: int) -> Optional[pd.DataFrame]:
        sync_start, sync_end = self._get_sync_range(max_days)
        if sync_start + self.period >= sync_end:  # Skip if no new data
            return
        return self.tardis_client.generate_candles(
            symbol=self.SYMBOL,
            from_datetime=sync_start,
            to_datetime=sync_end,
            candle_interval=self.period,
        )
