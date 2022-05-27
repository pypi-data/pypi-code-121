"""SQL query algorithm."""
from __future__ import annotations

from typing import Any, ClassVar, List, Optional, cast

from marshmallow import fields
import pandas as pd
import pandasql

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.exceptions import DuplicateColumnError
from bitfount.federated.algorithms.base import (
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _SQLAlgorithmMixIn
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerAlgorithm):
    """Modeller side of the SqlQuery algorithm."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Simply returns results."""
        return results


class _WorkerSide(_BaseWorkerAlgorithm):
    """Worker side of the SqlQuery algorithm."""

    def __init__(self, *, query: str, table: Optional[str], **kwargs: Any) -> None:
        self.datasource: _BaseSource
        self.query = query
        self.table = table
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        datasource.load_data()
        self.datasource = datasource

    def run(self) -> pd.DataFrame:
        """Executes the query on the data source and returns a dataframe."""
        if self.datasource.multi_table and isinstance(self.datasource, DatabaseSource):
            # Connect to the db directly if you are working with a multitable.
            conn = self.datasource.con.connect()
            output = pd.read_sql(sql=self.query, con=conn)
        else:
            # For SQL queries on a dataframe/ single table.
            self.datasource.load_data(table_name=self.table)
            df = self.datasource.data

            if ("from df" not in self.query) and ("FROM df" not in self.query):
                raise ValueError(
                    "The default table is called 'df'.",
                    "Please ensure your SQL query operates on that table.",
                )

            try:
                # We assume that the query includes something like 'from df'.
                output = pandasql.sqldf(self.query, {"df": df})
            except pandasql.PandaSQLException as ex:
                raise ValueError(
                    f"Error executing SQL query: [{self.query}], got error [{ex}]"
                )
        if any(output.columns.duplicated()):
            raise DuplicateColumnError(
                f"The following column names are duplicated in the output "
                f"dataframe: {output.columns[output.columns.duplicated()]}. "
                f"Please rename them in the query, and try again."
            )
        return cast(pd.DataFrame, output)


class SqlQuery(_BaseAlgorithmFactory, _SQLAlgorithmMixIn):
    """Simple algorithm for running a SQL query on a table.

    Args:
        query: The SQL query to execute.

    Attributes:
        name: The name of the algorithm.
        field: The name of the column to take the mean of.
    """

    def __init__(self, *, query: str, **kwargs: Any):
        super().__init__()
        self.query = query
        self.table: Optional[str] = kwargs.get("table")

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "query": fields.Str(),
        "table": fields.Str(allow_none=True),
    }

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the SqlQuery algorithm."""
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the SqlQuery algorithm."""
        return _WorkerSide(query=self.query, table=self.table, **kwargs)
