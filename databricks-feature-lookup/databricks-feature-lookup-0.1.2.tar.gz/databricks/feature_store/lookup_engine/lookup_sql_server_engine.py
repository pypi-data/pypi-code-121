from databricks.feature_store.entities.online_feature_table import OnlineFeatureTable
from databricks.feature_store.lookup_engine.lookup_sql_engine import (
    LookupSqlEngine,
)

import collections


class LookupSqlServerEngine(LookupSqlEngine):
    def __init__(
        self, online_feature_table: OnlineFeatureTable, ro_user: str, ro_password: str
    ):
        super().__init__(online_feature_table, ro_user, ro_password)

    @property
    def engine_url(self):
        return f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}?driver=ODBC+Driver+17+for+SQL+Server"

    @classmethod
    def _sql_safe_name(cls, name):
        # MSSQL requires [xxx] format to safely handle identifiers that contain special characters or are reserved words.
        return f"[{name}]"

    def _database_contains_feature_table(self):
        import sqlalchemy

        query = sqlalchemy.sql.text(
            f"SELECT {self.TABLE_NAME} FROM {self.INFORMATION_SCHEMA}.{self.TABLES} "
            f"WHERE {self.TABLE_CATALOG}='{self.database_name}' AND {self.TABLE_NAME} IN ('{self.table_name}')"
        )
        results = self._run_sql_query(query)
        table = results.fetchall()
        return len(table) > 0

    def _database_contains_primary_keys(self):
        import sqlalchemy

        query = sqlalchemy.sql.text(
            f"SELECT col.{self.COLUMN_NAME} FROM {self.INFORMATION_SCHEMA}.{self.TABLE_CONSTRAINTS} tab, {self.INFORMATION_SCHEMA}.{self.CONSTRAINT_COLUMN_USAGE} col "
            f"WHERE tab.{self.TABLE_CATALOG}='{self.database_name}' AND col.{self.TABLE_CATALOG}='{self.database_name}' AND "
            f"col.{self.CONSTRAINT_NAME}=tab.{self.CONSTRAINT_NAME} AND col.{self.TABLE_NAME}=tab.{self.TABLE_NAME} AND "
            f"{self.CONSTRAINT_TYPE}='PRIMARY KEY' AND col.{self.TABLE_NAME}='{self.table_name}'"
        )
        results = self._run_sql_query(query)
        primary_keys = [r[0] for r in results.fetchall()]
        return collections.Counter(primary_keys) == collections.Counter(
            [primary_key.name for primary_key in self.primary_keys]
        )
