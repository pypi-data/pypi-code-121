from databricks.feature_store.entities.online_feature_table import OnlineFeatureTable
from databricks.feature_store.lookup_engine.lookup_sql_engine import (
    LookupSqlEngine,
)
from databricks.feature_store.entities.cloud import Cloud

import collections


class LookupMySqlEngine(LookupSqlEngine):

    PRIMARY_COLUMN_KEY = "PRI"

    def __init__(
        self, online_feature_table: OnlineFeatureTable, ro_user: str, ro_password: str
    ):
        super().__init__(online_feature_table, ro_user, ro_password)

    @property
    def engine_url(self):
        if self.online_store.cloud == Cloud.AZURE:
            """
            Construct an engine URL in the format that Azure mysql expects, where the user portion
            of the connection string is in the <username@hostname> format.  The rationale for this
            format is described in the Azure docs here: https://bit.ly/3BGBBFF.

            This function expects self.host to be in the format: <servername>.mysql.database.azure.com, which is the expected
            format according to the Azure docs mentioned above.
            """
            if "." in self.host:
                hostname = self.host.split(".")[0]
            else:
                raise ValueError(
                    "AzureMySql host not in the expected format: <servername>.mysql.database.azure.com"
                )
            username = f"{self.user}@{hostname}"
        else:
            username = self.user

        return f"mysql+pymysql://{username}:{self.password}@{self.host}:{self.port}/{self.database_name}"

    @classmethod
    def _sql_safe_name(cls, name):
        # MySQL requires `xxx` format to safely handle identifiers that contain special characters or are reserved words.
        return f"`{name}`"

    def _database_contains_feature_table(self):
        import sqlalchemy

        query = sqlalchemy.sql.text(
            f"SELECT {self.TABLE_NAME} FROM {self.INFORMATION_SCHEMA}.{self.TABLES} "
            f"WHERE {self.TABLE_SCHEMA}='{self.database_name}' AND {self.TABLE_NAME} IN ('{self.table_name}')"
        )
        results = self._run_sql_query(query)
        table = results.fetchall()
        return len(table) > 0

    def _database_contains_primary_keys(self):
        import sqlalchemy

        query = sqlalchemy.sql.text(
            f"SELECT {self.COLUMN_NAME} FROM {self.INFORMATION_SCHEMA}.{self.COLUMNS} "
            f"WHERE {self.TABLE_SCHEMA}='{self.database_name}' AND {self.TABLE_NAME}='{self.table_name}' "
            f"AND {self.COLUMN_KEY}='{self.PRIMARY_COLUMN_KEY}'"
        )
        results = self._run_sql_query(query)
        primary_keys = [r[0] for r in results.fetchall()]
        return collections.Counter(primary_keys) == collections.Counter(
            [primary_key.name for primary_key in self.primary_keys]
        )
