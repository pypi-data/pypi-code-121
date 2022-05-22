import copy
import threading

from worker_bunch.database.database_connector import DatabaseConnector
from worker_bunch.service_config import ConfigException


class DatabaseManager:

    def __init__(self, config):

        self._config = copy.deepcopy(config)
        self._lock = threading.Lock()

    def create(self, context_name: str, connection_key: str) -> DatabaseConnector:
        with self._lock:
            connection_config = self._config.get(connection_key)
            if not connection_config:
                raise ConfigException(f"Unknown database connection ({connection_key}) requested!")

            connection_config = copy.deepcopy(connection_config)
            database = DatabaseConnector(connection_config, context_name, connection_key)
            return database
