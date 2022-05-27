"""Module containing DatabaseSource class.

DatabaseSource class handles loading data stored in a SQL database.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Union, cast

import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import MetaData, Table, text
from sqlalchemy.orm import Session

from bitfount.data.datasources.base_source import _MultiTableSource
from bitfount.data.utils import (
    DatabaseConnection,
    _convert_python_dtypes_to_pandas_dtypes,
)
from bitfount.types import _Dtypes

logger = logging.getLogger(__name__)


_DATABASE_PARTITION_SIZE: int = 100
_DATABASE_MAX_ROW_BUFFER: int = 500


class DatabaseSource(_MultiTableSource):
    """Data source for loading data from databases."""

    def __init__(
        self,
        db_conn: DatabaseConnection,
        database_partition_size: int = _DATABASE_PARTITION_SIZE,
        max_row_buffer: int = _DATABASE_MAX_ROW_BUFFER,
        **kwargs: Any,
    ):
        self.db_conn: DatabaseConnection = db_conn
        self.database_partition_size = database_partition_size
        self.max_row_buffer = max_row_buffer
        self._con: Optional[sqlalchemy.engine.Engine] = None
        self.datastructure_query: Optional[str] = None
        self.datastructure_table_name: Optional[str] = None

    @property
    def table_names(self) -> List[str]:
        """Database table names."""
        return self.db_conn.table_names

    @property
    def query(self) -> Optional[str]:
        """A Database query as a string.

        The query is resolved in the following order:
            1. The query specified in the database connection.
            2. The table name specified in the database connection if just 1 table.
            3. The query specified by the datastructure (if multi-table).
            4. The table name specified by the datastructure (if multi-table).
            5. None.
        """
        if self.db_conn.query:
            return self.db_conn.query
        elif self.db_conn.table_names and len(self.db_conn.table_names) == 1:
            # Table name has been validated
            return f"SELECT * FROM {self.db_conn.table_names[0]}"  # nosec
        elif self.datastructure_query:
            return self.datastructure_query
        elif self.datastructure_table_name:
            # Table name has been validated
            return f"SELECT * FROM {self.datastructure_table_name}"  # nosec

        return None

    @property
    def con(self) -> sqlalchemy.engine.Engine:
        """Sqlalchemy engine.

        Connection options are set to stream results using a server side cursor where
        possible (depends on the database backend's support for this feature) with a
        maximum client side row buffer of `self.max_row_buffer` rows.
        """
        if not self._con:
            self._con = self.db_conn.con.execution_options(
                stream_results=True, max_row_buffer=self.max_row_buffer
            )
        return self._con

    def __len__(self) -> int:
        if self._data_is_loaded:
            return len(self.data)
        elif not self.db_conn.multi_table:
            data = self.get_data()
            assert data is not None  # nosec
            self.data = data
            return len(self.data)

        with self.con.connect() as con:
            # Ignoring the security warning because the sql query is trusted and
            # will be executed regardless.
            result = con.execute(
                text(f"SELECT COUNT(*) FROM ({self.query}) q")  # nosec
            )
            return cast(int, result.scalar_one())

    def _validate_table_name(self, table_name: Optional[str]) -> None:
        """Validate the table name exists in the database.

        Args:
            table_name: The name of the table.

        Raises:
            ValueError: If the data is multi-table but no table name provided.
            ValueError: If the table name is not found in the data.
            ValueError: If the database connection does not have any table names.
        """
        if table_name is None:
            raise ValueError("No table name provided for multi-table datasource.")
        elif not self.table_names:
            raise ValueError("Database Connection is not aware of any tables.")
        elif table_name not in self.table_names:
            raise ValueError(
                f"Table name {table_name} not found in the data. "
                f"Available tables: {self.table_names}"
            )

    def get_values(
        self, col_names: List[str], table_name: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in Database dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.
            table_name: The name of the table to which the column exists. Required
                for multi-table databases.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.
        """
        metadata = MetaData(self.con)
        output: Dict[str, Iterable[Any]] = {}
        if self.query is not None:
            # TODO: [BIT-1595] change to load memory using sqlalchemy FrozenResult
            self.data = cast(pd.DataFrame, pd.read_sql(self.query, con=self.con))
            for col_name in col_names:
                output[col_name] = self.data[col_name].unique()
        else:
            self._validate_table_name(table_name)

            table = Table(
                table_name,
                metadata,
                schema=self.db_conn.db_schema,
                autoload=True,
                autoload_with=self.con,
            )
            with Session(self.con) as session:
                for col_name in col_names:
                    values = np.array(
                        [v for v, in session.query(table.columns[col_name]).distinct()]
                    )
                    output[col_name] = values
        return output

    def get_column(
        self, col_name: str, table_name: Optional[str] = None, **kwargs: Any
    ) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from Database dataset.

        Args:
            col_name: The name of the column which should be loaded.
            table_name: The name of the table to which the column exists. Required
                for multi-table databases.

        Returns:
            The column requested as a series.

        Raises:
            ValueError: If the data is multi-table but no table name provided.
            ValueError: If the table name is not found in the data.
        """
        results: Iterable[Any]
        metadata = MetaData(self.con)
        if self.query is not None:
            with Session(self.con) as session:
                results = session.execute(text(self.query)).columns(col_name)
        else:
            self._validate_table_name(table_name)
            table = Table(
                table_name,
                metadata,
                schema=self.db_conn.db_schema,
                autoload=True,
                autoload_with=self.con,
            )
            with Session(self.con) as session:
                results = session.query(table.columns[col_name])

        series = pd.Series([v for v, in results])
        return series

    def get_data(
        self,
        sql_query: Optional[str] = None,
        table_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[pd.DataFrame]:
        """Loads and returns data from Database dataset.

        Args:
            sql_query: A SQL query string required for multi table data sources. This
                comes from the DataStructure and takes precedence over the table_name.
            table_name: Table name for multi table data sources. This
                comes from the DataStructure and is ignored if sql_query has been
                provided.

        Returns:
            A DataFrame-type object which contains the data.
        """
        data: Optional[pd.DataFrame] = None
        if self.db_conn.multi_table:
            # If multi-table, we don't actually load the data, we just set the query and
            # table name for the iterator.
            if sql_query is not None:
                self.datastructure_query = sql_query
            if table_name is not None:
                self.datastructure_table_name = table_name
        elif self.db_conn.query:
            data = pd.read_sql_query(sql=self.db_conn.query, con=self.con)
        else:
            # If the data is not multi-table and there is no query, there must
            # necessarily be one table name. Reassuring mypy of this.
            assert self.table_names is not None and len(self.table_names) == 1  # nosec
            query = f"SELECT * FROM {self.table_names[0]}"  # nosec
            data = pd.read_sql_query(
                sql=query,
                con=self.con,
            )
        return data

    def get_dtypes(self, table_name: Optional[str] = None, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types from the Database dataset.

        Args:
            table_name: The name of the table_name which should be loaded. Only
                required for multitable database.

        Returns:
            A mapping from column names to column types.
        """
        metadata = MetaData(self.con)
        dtypes: _Dtypes
        if self.query is not None:
            with Session(self.con) as session:
                result = session.execute(text(self.query)).first()
            data = pd.DataFrame([result])
            dtypes = data.convert_dtypes().dtypes.to_dict()

        else:
            self._validate_table_name(table_name)

            table = Table(
                table_name,
                metadata,
                schema=self.db_conn.db_schema,
                autoload=True,
                autoload_with=self.con,
            )
            dtypes = {
                col.name: _convert_python_dtypes_to_pandas_dtypes(
                    col.type.python_type, col.name
                )
                for col in table.columns
            }
        return dtypes

    @property
    def multi_table(self) -> bool:
        """Attribute to specify whether the datasource is multi table."""
        return self.db_conn.multi_table
