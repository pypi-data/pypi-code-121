from collections import defaultdict
from typing import Dict, List

from dropland.core.loaders.backend import BackendLoader
from dropland.storages.sql.base import SqlStorageBackend, SqlStorageType


class SqlBackendLoader(BackendLoader[SqlStorageBackend]):
    def __init__(self):
        super().__init__('dropland.storages.sql', 'create_sql_storage_backend')
        self._db_support_dict: Dict[SqlStorageType, List[str]] = defaultdict(list)

    def on_load(self, backend: SqlStorageBackend):
        for db_type in backend.db_supports:
            self._db_support_dict[db_type].append(backend.name)

    def get_backends_for_db(self, db_type: SqlStorageType) -> List[str]:
        return self._db_support_dict.get(db_type, [])
