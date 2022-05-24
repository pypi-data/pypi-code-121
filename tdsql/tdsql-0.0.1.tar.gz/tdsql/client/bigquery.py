from google.cloud import bigquery
import pandas as pd

from tdsql.client.base import BaseClient
from tdsql.test_config import TdsqlTestConfig

_CLIENT = bigquery.Client()


class BigQueryClient(BaseClient):
    def __init__(self) -> None:
        # See https://googleapis.dev/python/google-api-core/latest/auth.html#authentication # noqa
        self.client = _CLIENT

    def select(self, sql: str, config: TdsqlTestConfig) -> pd.DataFrame:
        query_job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=config.max_bytes_billed,
            use_legacy_sql=False,
        )
        df = self.client.query(sql, job_config=query_job_config).to_dataframe()
        return df
