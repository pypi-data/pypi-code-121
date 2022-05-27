"""
API Read Functions
"""
from typing import List, Optional

import pandas as pd

from pyrasgo import errors
from pyrasgo.primitives import Dataset


class Read:
    """
    API Read Class
    """

    def __init__(self):
        from pyrasgo.api import Get
        from pyrasgo.api.connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()
        self._dw = None

    @property
    def data_warehouse(self):
        from pyrasgo.storage import DataWarehouse, dw_connection

        if not self._dw:
            self._dw: DataWarehouse = dw_connection(self.api._dw_type())
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
            raise errors.ParameterValueError(
                message="Must pass either a valid dataset ID or Dataset object to read into a DataFrame"
            )
        if not dataset:
            # Note: Func below already raises API error if dataset with id doesn't exist
            dataset = self.get.dataset(id)

        # Require the operation set on the DS to make
        # sure table is created before reading
        dataset._get_or_create_op_set()

        # Get the FQTN from snapshot or current dataset
        if snapshot_index:
            try:
                fqtn = dataset._api_dataset.snapshots[snapshot_index].fqtn
            except IndexError as err:
                raise errors.RasgoResourceException(f"Snapshot index {snapshot_index} does not exist") from err
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
            except Exception as err:
                raise errors.DWResourceException(f"Dataset table is not reachable: {err}") from err
