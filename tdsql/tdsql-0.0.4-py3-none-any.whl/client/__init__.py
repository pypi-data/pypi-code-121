from tdsql.exception import InvalidInputError
from tdsql.client.base import BaseClient


def get_client(database: str) -> BaseClient:
    if database == "bigquery":
        from tdsql.client import bigquery

        return bigquery.BigQueryClient()
    else:
        raise InvalidInputError(f"{database} is not supported")
