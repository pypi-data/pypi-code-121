""" Defines the LookupSqlEngine class, which is used to perform
lookups on SQL databases. This class differs from PublishSqlEngine in that
its actions are read-only, and uses a Python connector instead of Java.
"""

from databricks.feature_store.lookup_engine.lookup_engine import LookupEngine
from databricks.feature_store.entities.online_feature_table import OnlineFeatureTable
from databricks.feature_store.entities.online_store_for_serving import (
    MySqlConf,
    SqlServerConf,
)
from databricks.feature_store.entities.data_type import DataType
from databricks.feature_store.utils.data_type_details_utils import parse_decimal_details


import abc
import collections
import functools
import logging
import numpy as np
import pandas as pd
from typing import List
from contextlib import contextmanager
import json
from decimal import Context
import re

_logger = logging.getLogger(__name__)

SQL_DATA_TYPES_REQUIRE_JSON_DESERIALIZATION = {DataType.ARRAY, DataType.MAP}
SQL_DATA_TYPES_REQUIRE_PRECISION = {DataType.DECIMAL}


class LookupSqlEngine(LookupEngine):
    INFORMATION_SCHEMA = "INFORMATION_SCHEMA"
    TABLES = "TABLES"
    TABLE_CATALOG = "TABLE_CATALOG"
    TABLE_SCHEMA = "TABLE_SCHEMA"
    TABLE_NAME = "TABLE_NAME"
    COLUMNS = "COLUMNS"
    COLUMN_NAME = "COLUMN_NAME"
    COLUMN_KEY = "COLUMN_KEY"
    DATA_TYPE = "DATA_TYPE"
    TABLE_CONSTRAINTS = "TABLE_CONSTRAINTS"
    CONSTRAINT_COLUMN_USAGE = "CONSTRAINT_COLUMN_USAGE"
    CONSTRAINT_TYPE = "CONSTRAINT_TYPE"
    CONSTRAINT_NAME = "CONSTRAINT_NAME"

    @abc.abstractmethod
    def __init__(
        self, online_feature_table: OnlineFeatureTable, ro_user: str, ro_password: str
    ):
        self.online_store = online_feature_table.online_store
        (
            self.database_name,
            self.table_name,
        ) = online_feature_table.online_feature_table_name.split(".")
        self.user = ro_user
        self.password = ro_password
        self.host = self.online_store.extra_configs.host
        self.port = self.online_store.extra_configs.port

        self.primary_keys = online_feature_table.primary_keys
        self.feature_names_to_feature_details = {
            f.name: f for f in online_feature_table.features
        }

        self._validate_online_feature_table()

    @contextmanager
    def _get_connection(self):

        # Everything between here and the yield statement will be executed in contextmanager.__enter__()
        import sqlalchemy

        engine = sqlalchemy.create_engine(self.engine_url)
        connection = engine.connect()

        # When the caller invokes "with _get_connection() as x", the connection will be returned as "x"
        yield connection

        # Everything below here will be executed in contextmanager.__exit__()
        connection.close()

    @property
    def engine_url(self) -> str:
        raise NotImplementedError

    def lookup_features(
        self, lookup_df: pd.DataFrame, feature_names: List[str]
    ) -> pd.DataFrame:
        import sqlalchemy

        pk_filter_phrase = " AND ".join(
            [f"{self._sql_safe_name(pk)} = :{pk}" for pk in lookup_df.columns]
        )
        select_feat_phrase = ", ".join(
            f"{self._sql_safe_name(f)}" for f in feature_names
        )
        query = sqlalchemy.sql.text(
            f"SELECT {select_feat_phrase} FROM {self._sql_safe_name(self.table_name)} WHERE {pk_filter_phrase}"
        )
        sql_query = functools.partial(self._run_lookup_sql_query, query, feature_names)
        # TODO: Optimize the SQL query by batching: https://databricks.atlassian.net/browse/ML-16636
        feature_df = lookup_df.apply(sql_query, axis=1, result_type="expand")
        feature_df.columns = feature_names
        for feature in feature_names:
            feature_data_type = self.feature_names_to_feature_details[feature].data_type
            if feature_data_type in SQL_DATA_TYPES_REQUIRE_JSON_DESERIALIZATION:
                feature_df[feature] = feature_df[feature].map(
                    lambda x: json.loads(x) if x else x, na_action="ignore"
                )
            elif feature_data_type in SQL_DATA_TYPES_REQUIRE_PRECISION:
                feature_data_type_details = json.loads(
                    self.feature_names_to_feature_details[feature].data_type_details
                )
                precision, _ = parse_decimal_details(feature_data_type_details)
                feature_df[feature] = feature_df[feature].map(
                    lambda x: Context(prec=precision).create_decimal(str(x))
                    if x
                    else x,
                    na_action="ignore",
                )
        return feature_df

    def _validate_online_feature_table(
        self,
    ) -> None:
        # Validate the Python database connection specified by the database location in OnlineFeatureTable.
        # Throw operational error if new connection is invalid
        try:
            with self._get_connection():
                pass
        except Exception as e:
            raise ValueError(f"Connection could not be established: {str(e)}.")

        # Validate the online feature table exists in online database as specified by the OnlineFeatureTable.
        if not self._database_contains_feature_table():
            raise ValueError(
                f"Table {self.table_name} does not exist in database {self.database_name}."
            )

        # Validate the online feature table has the same primary keys specified by the OnlineFeatureTable.
        if not self._database_contains_primary_keys():
            raise ValueError(
                f"Table {self.table_name} does not contain primary keys {self.primary_keys}."
            )

    def shutdown(self) -> None:
        """
        Closes the database connection if it exists on the SQL lookup engine.
        :return:
        """
        self._close()

    def _close(self) -> None:
        """
        This is a no-op because a new sql connection is opened for each query and closed after the query executes.
        """
        pass

    def _run_lookup_sql_query(self, query, feature_names, lookup_row):
        """
        This helper function executes a single SQL query .
        """
        query_params = lookup_row.to_dict()
        sql_data = self._run_sql_query(query, query_params)
        feat_values = sql_data.fetchall()

        if len(feat_values) == 0:
            _logger.warning(
                f"No feature values found in {self.table_name} for {query_params}."
            )
            nan_features = np.empty(len(feature_names))
            nan_features[:] = np.nan
            return nan_features

        # Return the first result
        return feat_values[0]

    def _run_sql_query(self, query, query_params=None):
        with self._get_connection() as sql_connection:
            sql_data = sql_connection.execute(query, query_params)
        return sql_data

    @classmethod
    def _sql_safe_name(cls, name):
        raise NotImplementedError

    def _database_contains_feature_table(self):
        raise NotImplementedError

    def _database_contains_primary_keys(self):
        raise NotImplementedError
