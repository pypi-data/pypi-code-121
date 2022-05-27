from typing import List, Optional

import pandas as pd

from pyrasgo.primitives import Dataset
from .error import APIError


class Read:
    def __init__(self):
        from . import Get

        self.get = Get()
        self._dw = None

    @property
    def data_warehouse(self):
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        if self._dw:
            return self._dw
        self._dw: SnowflakeDataWarehouse = DataWarehouse.connect()
        return self._dw

    def dataset(
        self,
        id: Optional[int] = None,
        dataset: Optional[Dataset] = None,
        filters: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        snapshot_index: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Constructs and returns pandas DataFrame from the specified Rasgo Dataset

        You can supply SQL WHERE clause filters, order the dataset by columns, only
        return selected columns, and add a return limit as well

        Example:
            ```
            rasgo.read.dataset(
                id=74,
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY'],
                limit=50
            )
            ```

        Args:
            id: dataset id to read into df
            dataset: Dataset obj to read into df
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
            limit: Only return this many rows in the df
            snapshot: the index of a snapshot from Dataset.snapshots to read
        """
        # Validate one dataset passed in, id or dataset obj
        if not dataset and id is None:
            raise ValueError("Must pass either a valid dataset ID or Dataset object to read into a DataFrame")
        if not dataset:
            # Note: Func below already raises API error if dataset with id doesn't exist
            dataset = self.get.dataset(id)

        # Require the operation set on the DS to make
        # sure table is created before reading
        dataset._require_operation_set()

        # Get the FQTN from snapshot or current dataset
        if snapshot_index:
            try:
                fqtn = dataset._api_dataset.snapshots[snapshot_index].fqtn
            except IndexError:
                raise ValueError("Snapshot index does not exist")
        else:
            fqtn = dataset.fqtn

        if dataset:
            try:
                query = self.data_warehouse.make_select_statement(
                    table_metadata={'fqtn': fqtn},
                    filters=filters,
                    order_by=order_by,
                    columns=columns,
                    limit=limit,
                )
                return self.data_warehouse.query_into_dataframe(query)
            except Exception as e:
                raise APIError(f"Dataset table is not reachable: {e}")
