import contextlib
import enum
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional

from dropland.storages.base import StorageBackend, StorageEngine

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}


class SqlStorageType(str, enum.Enum):
    SQLITE = 'sqlite'
    POSTGRES = 'postgresql'
    MYSQL = 'mysql'


@dataclass
class EngineConfig:
    url: str
    echo: bool = False
    pool_min_size: int = 1
    pool_max_size: int = 8
    pool_expire_seconds: int = 60
    pool_timeout_seconds: int = 15


class SqlStorageBackend(StorageBackend):
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def db_supports(self) -> List[SqlStorageType]:
        raise NotImplementedError

    @property
    def connection_class(self) -> Optional[type]:
        raise NotImplementedError

    @property
    def async_connection_class(self) -> Optional[type]:
        raise NotImplementedError

    def create_engine(self, db_type: SqlStorageType, config: EngineConfig, use_async: bool) \
            -> Optional['SqlStorageEngine']:
        raise NotImplementedError


class SqlStorageEngine(StorageEngine):
    def __init__(self, backend: SqlStorageBackend, raw_engine, db_type: SqlStorageType, timeout: timedelta):
        super().__init__(backend)
        self._engine = raw_engine
        self._db_type = db_type
        self._timeout = timeout

    @property
    def raw_engine(self):
        return self._engine

    @property
    def db_type(self):
        return self._db_type

    @property
    def timeout(self) -> timedelta:
        return self._timeout

    # noinspection PyPep8Naming
    @property
    def Model(self) -> 'Model':
        raise NotImplementedError

    @property
    def metadata(self):
        raise NotImplementedError

    @contextlib.contextmanager
    def transaction_context(self, connection, autocommit: bool = True):
        raise NotImplementedError

    @contextlib.asynccontextmanager
    async def async_transaction_context(self, connection, autocommit: bool = True):
        raise NotImplementedError
