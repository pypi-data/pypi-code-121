import wrapt
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional, Union
from dictdiffer import diff, revert, patch
import json
from .exceptions import MongoengineMigrateError


class TransactionDict(wrapt.ObjectProxy):
    def __init__(self, wrapped=None):
        super().__init__(wrapped or dict())
        self._stub = wrapped.copy()
        self._txn_log = []

    @property
    def txn_log(self):
        return self._txn_log

    @txn_log.setter
    def txn_log(self, val):
        self._txn_log = val or []

    def rollback(self):
        # Items could get changed by reference, so check it additionally
        self.detect_changes()
        revert(self._txn_log, self.__wrapped__, True)
        revert(self._txn_log, self._stub, True)
        self._txn_log.clear()

    def commit(self):
        # Items could get changed by reference, so check it additionally
        self.detect_changes()
        self._txn_log.clear()

    def detect_changes(self):
        if self.__wrapped__ == self._stub:
            return

        d = diff(self.__wrapped__, self._stub)
        if d:
            self._txn_log.extend(d)
            patch(d, self._stub, True)

    def copy(self):
        res = TransactionDict(self.__wrapped__.copy())
        res.txn_log = self.txn_log.copy()

        return res

    def __getattr__(self, item):
        observe_methods = frozenset( ('clear', 'pop', 'popitem', 'setdefault', 'update'))
        res = getattr(self.__wrapped__, item)
        if item in observe_methods:
            self.detect_changes()

        return res

    def __getitem__(self, item):
        # Nested dict could be changed here
        res = self.__wrapped__.__getitem__(item)
        self.detect_changes()
        return res

    def __delattr__(self, item):
        res = self.__wrapped__.__delitem__(item)
        self.detect_changes()
        return res


class DBManager(wrapt.ObjectProxy):
    """Database manager which is used to manage db schema and state"""

    def __init__(self,
                 db: Database,
                 schema_collection: Collection,
                 schema:Optional[TransactionDict] = None):
        super().__init__(db)
        self.schema_collection = schema_collection
        self.schema = schema if schema is not None else self._load_db_schema()

    def get_collection_manager(self, collection_name: str):
        return CollectionManager(self.__wrapped__[collection_name], self, self.schema)

    def _write_db_schema(self, schema: TransactionDict):
        """
        Write schema to db
        :param schema: schema dict
        :return:
        """
        fltr = {'type': 'schema'}
        data = {'type': 'schema', 'value': schema}
        if schema.txn_log:
            data['txn_log'] = json.dumps(schema.txn_log)
        self.schema_collection.replace_one(fltr, data, upsert=True)

    def _load_db_schema(self) -> TransactionDict:
        """Load schema from db"""
        fltr = {'type': 'schema'}
        res = self.schema_collection.find_one(fltr) or {}

        schema = res.get('value', {})
        txn_log = json.loads(res.get('txn_log', 'null'))
        res = TransactionDict(schema)
        res.txn_log = txn_log

        return res


class CollectionManager(wrapt.ObjectProxy):
    def __init__(self,
                 wrapped: Collection,
                 db_manager: DBManager,
                 db_schema: TransactionDict):
        super().__init__(wrapped)
        self.db_schema = db_schema
        self.db_manager = db_manager
        self._txn_log_ptr = None
        self._orig_schema = None

    def start_or_rerun_txn(self):
        if self.db_schema.txn_log:
            self._orig_schema = self.db_schema.copy()
            self._txn_log_ptr = 0
            self.db_schema.rollback()

    def commit(self):
        if self._orig_schema is not None \
                and len(self._orig_schema.txn_log) <= len(self.db_schema.txn_log):
            if self._orig_schema != self.db_schema:
                raise MongoengineMigrateError('Restored transaction produced ')
        try:
            txn = self._orig_schema.txn_log[self._txn_log_ptr]
        except IndexError:
            txn = None