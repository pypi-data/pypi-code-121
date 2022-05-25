from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Set

from dependency_injector.wiring import inject

from dropland.storages.sql.base import EngineConfig, SqlStorageEngine, SqlStorageType
from dropland.storages.sql.loader import SqlBackendLoader


@dataclass
class EngineKey:
    db_type: SqlStorageType
    backend: str
    is_async: bool

    def __eq__(self, other: 'EngineKey'):
        return (self.db_type, self.backend, self.is_async) == (other.db_type, other.backend, other.is_async)

    def __hash__(self):
        return hash((self.db_type, self.backend, self.is_async))


@dataclass
class EngineWithDbType:
    db_type: SqlStorageType
    engine: SqlStorageEngine


@dataclass
class EngineWithBackend:
    backend: str
    engine: SqlStorageEngine


class EngineFactory:
    def __init__(self, backend_loader: SqlBackendLoader):
        self._backend_loader = backend_loader
        self._engines: Dict[EngineKey, SqlStorageEngine] = dict()
        self._engines_by_type: Dict[SqlStorageType, Set[str]] = defaultdict(set)
        self._engines_by_backend: Dict[str, Set[SqlStorageType]] = defaultdict(set)

    @inject
    def create_engine(
        self, db_type: SqlStorageType, config: EngineConfig,
            backend_name: Optional[str] = None, use_async: bool = False) -> Optional[SqlStorageEngine]:
        uri = config.url

        if use_async:
            if db_type == SqlStorageType.SQLITE:
                uri = uri.replace('sqlite', 'sqlite+aiosqlite', 1)
            elif db_type == SqlStorageType.POSTGRES:
                uri = uri.replace('postgresql', 'postgresql+asyncpg', 1)
            elif db_type == SqlStorageType.MYSQL:
                uri = uri.replace('mysql', 'mysql+aiomysql', 1)
        else:
            if db_type == SqlStorageType.MYSQL:
                uri = uri.replace('mysql', 'mysql+pymysql', 1)

        config = replace(config, url=uri)
        self._backend_loader.load_backends()

        backends = self._backend_loader.get_backends_for_db(db_type)
        if len(backends) < 1:
            return None

        backend = None

        if backend_name:
            for b in backends:
                if b == backend_name:
                    backend = self._backend_loader.get_backend(b)
                    break
        else:
            backend_name = backends[0]
            backend = self._backend_loader.get_backend(backend_name)

        if not backend:
            return None

        if engine := self._engines.get(EngineKey(db_type=db_type, backend=backend_name, is_async=use_async)):
            return engine
        else:
            engine = backend.create_engine(db_type, config, use_async)

        if not engine:
            return None

        self._engines[EngineKey(db_type=db_type, backend=backend_name, is_async=use_async)] = engine
        self._engines_by_type[db_type].add(backend_name)
        self._engines_by_backend[backend_name].add(db_type)
        return engine

    def get_engine(self, db_type: SqlStorageType, backend_name: str, is_async: bool = False) \
            -> Optional[SqlStorageEngine]:
        return self._engines.get(EngineKey(db_type=db_type, backend=backend_name, is_async=is_async))

    def get_engines_for_type(self, db_type: SqlStorageType, is_async: bool) -> List[EngineWithDbType]:
        backends = self._engines_by_type.get(db_type, set())
        engines = [self.get_engine(db_type, b, is_async) for b in backends]
        return [EngineWithDbType(db_type=db_type, engine=e) for e in engines if e is not None]

    def get_engines_for_backend(self, backend_name: str, is_async: bool) -> List[EngineWithBackend]:
        db_types = self._engines_by_backend.get(backend_name, set())
        engines = [self.get_engine(t, backend_name, is_async) for t in db_types]
        return [EngineWithBackend(backend=backend_name, engine=e) for e in engines if e is not None]

    def get_backend_names(self) -> List[str]:
        return list(self._engines_by_backend.keys())
