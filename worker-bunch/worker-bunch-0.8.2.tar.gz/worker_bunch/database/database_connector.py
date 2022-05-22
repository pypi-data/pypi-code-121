import abc
import datetime
import logging
from logging import Logger
from typing import Optional

import psycopg
from tzlocal import get_localzone

from worker_bunch.database.database_config import DatabaseConfKey
from worker_bunch.service_logging import ServiceLogging
from worker_bunch.utils.time_utils import TimeUtils


class DatabaseException(Exception):
    pass


class DatabaseConnector(abc.ABC):

    def __init__(self, config, context_name: str, connection_key: str):

        self._context_name = context_name
        self._connection_key = connection_key
        self.__logger = None  # type: Optional[Logger]

        self._connection = None
        self._auto_commit = config.get(DatabaseConfKey.AUTO_COMMIT, False)
        self._last_connect_time = None  # type: Optional[datetime.datetime]

        # configuration
        self._connect_data = {
            "host": config[DatabaseConfKey.HOST],
            "port": config[DatabaseConfKey.PORT],
            "user": config[DatabaseConfKey.USER],
            "password": config.get(DatabaseConfKey.PASSWORD),
            "dbname": config[DatabaseConfKey.DATABASE],
        }

        self._timezone = config.get(DatabaseConfKey.TIMEZONE)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    @property
    def _logger(self):
        if self.__logger is None:
            log_name = f"{self._context_name}-{self._connection_key}"
            log_name = ServiceLogging.get_log_name(self, log_name)
            self.__logger = logging.getLogger(log_name)
        return self.__logger

    @property
    def is_connected(self):
        return bool(self._connection)

    @property
    def connection(self):
        return self._connection

    def connect(self):
        if self._connection:
            self._connection.close()

        try:
            self._connection = psycopg.connect(**self._connect_data, autocommit=self._auto_commit)

            with self._connection.cursor() as cursor:
                time_zone = self._timezone if self._timezone else self.get_default_time_zone_name()
                stmt = "set timezone='{}'".format(time_zone)
                try:
                    cursor.execute(stmt)
                except Exception:
                    self._logger.error("setting timezone failed (%s)!", stmt)
                    raise

            self._last_connect_time = TimeUtils.now()

        except psycopg.OperationalError as ex:
            raise DatabaseException(str(ex)) from ex

    def close(self):
        try:
            if self._connection:
                self._connection.close()
        except Exception as ex:
            self._logger.exception(ex)
        finally:
            self._connection = None

    @classmethod
    def get_default_time_zone_name(cls):
        local_timezone = get_localzone()
        if not local_timezone:
            local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        return str(local_timezone)
