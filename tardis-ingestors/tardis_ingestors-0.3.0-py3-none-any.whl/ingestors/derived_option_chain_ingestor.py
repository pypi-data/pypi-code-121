from datetime import datetime
from typing import Optional

import pandas as pd
from tardis.ingestors.option_chain_ingestor import OptionsChainTardisIngestor
from tardis.models.exchange.grouped_symbols import GroupedSymbol


class DerivedOptionsChainTardisIngestor(OptionsChainTardisIngestor):
    SYMBOL = GroupedSymbol.OPTIONS.value
    TABLE_TYPE = "derivedchain"

    def _get_data(
        self, max_days: int, first_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        sync_start, sync_end = self._get_sync_range(max_days, first_date)
        if sync_start + self.period >= sync_end:  # Skip if no new data
            return

        return self.tardis_client.generate_derived_option_chain_snapshots(
            from_datetime=sync_start,
            to_datetime=sync_end,
            snapshot_interval=self.period,
            previous_snapshot=self._get_latest_snapshot(),
        ).drop(columns=["exchange"])
