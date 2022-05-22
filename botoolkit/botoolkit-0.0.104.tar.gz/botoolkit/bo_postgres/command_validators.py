from abc import (
    abstractmethod,
)

import psycopg2

from botoolkit.bo_postgres.helpers import (
    DBQueryExecutor,
)


class BaseDBValidator:
    """
    Базовый класс валидаторов базы данных
    """

    def __init__(
        self,
        db_executor: DBQueryExecutor,
    ):
        self._db_executor = db_executor

    @abstractmethod
    def validate(self):
        pass


class LocalDBAccessValidator(BaseDBValidator):
    """
    Валидатор доступности подключения к базе данных по указанным параметрам с
    локальной машины
    """

    def validate(self):
        have_access = False

        try:
            self._db_executor.execute(
                raw_sql='SELECT 1;'
            )

            have_access = True
        except psycopg2.OperationalError:
            pass

        return have_access


class LocalDBMaxConnectionsValidator(BaseDBValidator):
    """
    Проверяет максимальное количество подключений к БД
    """

    def validate(self):
        max_connections = None

        try:
            max_connections = self._db_executor.fetchone(
                raw_sql='SELECT current_setting(\'max_connections\');'
            )[0]
        except psycopg2.OperationalError:
            pass

        return max_connections


class LocalDBMaxParallelWorkersPerGatherValidator(BaseDBValidator):
    """
    Проверяет максимальное количество подключений к БД
    """

    def validate(self):
        max_parallel_workers_per_gather = None

        try:
            max_parallel_workers_per_gather = self._db_executor.fetchone(
                raw_sql=(
                    'SELECT current_setting(\'max_parallel_workers_per_gather\');'
                ),
            )[0]
        except psycopg2.OperationalError:
            pass

        return max_parallel_workers_per_gather

