from pymysql import DatabaseError

from feast.protos.feast.core.Registry_pb2 import Registry as RegistryProto
from feast.registry_store import RegistryStore
from feast.repo_config import RegistryConfig
from .mysql_config import MySQLConfig
from .utils import _get_conn, get_cur


class MySQLRegistryStore(RegistryStore):
    def __init__(self, config: RegistryConfig, registry_path: str):
        self.db_config = (
            MySQLConfig(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
            )
            if config.database
            else MySQLConfig(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
            )
        )
        self.table_name = config.path
        self.cache_ttl_seconds = config.cache_ttl_seconds

    def get_registry_proto(self) -> RegistryProto:
        registry_proto = RegistryProto()
        with _get_conn(self.db_config) as conn, get_cur(conn) as cur:
            query = (
                f"SELECT registry FROM {self.table_name}  WHERE version = "
                f"(SELECT max(version) FROM {self.table_name})"
            )
            try:
                cur.execute(query)
                row = cur.fetchone()
                if row:
                    registry_proto = registry_proto.FromString(row[0])
            except DatabaseError:
                pass
        return registry_proto

    def update_registry_proto(self, registry_proto: RegistryProto):
        """
        Overwrites the current registry proto with the proto passed in. This method
        writes to the registry path.

        Args:
            registry_proto: the new RegistryProto
        """
        with _get_conn(self.db_config) as conn, get_cur(conn) as cur:
            create_table_query = (
                f"CREATE TABLE IF NOT EXISTS {self.table_name} (version BIGSERIAL "
                f"PRIMARY KEY, registry BYTEA NOT NULL);"
            )
            cur.execute(create_table_query)

            # Do we want to keep track of the history or just keep the latest?
            insert_query = (
                f"INSERT INTO {self.table_name} (registry) VALUES "
                f"({[registry_proto.SerializeToString()]});"
            )
            cur.execute(insert_query)

    def teardown(self):
        with _get_conn(self.db_config) as conn, get_cur(conn) as cur:
            query = f"DROP TABLE IF EXISTS {self.table_name};"
            cur.execute(query)
