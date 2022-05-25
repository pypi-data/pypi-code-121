import json
import platform
from urllib.parse import urlparse

from openlineage.airflow.utils import (
    get_connection_uri,
    get_normalized_postgres_connection_uri
)

""" This helper is created to provide uniform naming conventions
across several metadata extractor. Also the helper provided here
comply with OpenLineage naming specification. For more details
please visit:
https://github.com/OpenLineage/OpenLineage/blob/main/spec/Naming.md
"""


def fs_scheme() -> str:
    return 'file'


def fs_authority() -> str:
    return platform.uname().node


def fs_connection_uri(path) -> str:
    scheme = fs_scheme()
    host = platform.uname().node
    return f'{scheme}://{host}{path}'


def pg_scheme() -> str:
    return 'postgres'


def pg_authority(conn) -> str:
    if conn.host and conn.port:
        return f'{conn.host}:{conn.port}'
    else:
        parsed = urlparse(conn.get_uri())
        return f'{parsed.hostname}:{parsed.port}'


def pg_connection_uri(conn) -> str:
    return get_normalized_postgres_connection_uri(conn)


def mysql_scheme() -> str:
    return 'mysql'


def mysql_authority(conn) -> str:
    if conn.host and conn.port:
        return f'{conn.host}:{conn.port}'
    else:
        parsed = urlparse(conn.get_uri())
        return f'{parsed.host}:{parsed.port}'


def mysql_connection_uri(conn) -> str:
    return get_connection_uri(conn)


def mongo_scheme() -> str:
    return 'mongo'


def mongo_authority(conn) -> str:
    if conn.host and conn.port:
        return f'{conn.host}:{conn.port}'
    else:
        parsed = urlparse(conn.get_uri())
        return f'{parsed.host}:{parsed.port}'


def mongo_connection_uri(conn) -> str:
    return get_connection_uri(conn)


def gcs_scheme() -> str:
    return 'gs'


def gcs_authority(bucket) -> str:
    return f"{bucket}"


def gcs_connection_uri(bucket, path) -> str:
    return f"{gcs_scheme()}://{bucket}{path}"


def bq_scheme() -> str:
    return 'bigquery'


def bq_authority(conn) -> str:
    return ""


def bq_connection_uri(conn, dataset, table) -> str:
    scheme = bq_scheme()
    extras = json.loads(conn.get_extra())
    return f"{scheme}:{extras['extra__google_cloud_platform__project']}.{dataset}.{table}"