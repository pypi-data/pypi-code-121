import psycopg2.extensions
from django.db import OperationalError, connection
from django.db.transaction import DEFAULT_DB_ALIAS, Atomic
from psycopg2.errorcodes import SERIALIZATION_FAILURE


def serializable_atomic(using=None, savepoint=True):
    return atomic(using, savepoint, psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)


def atomic(using=None, savepoint=True, isolation_level=psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT):
    if callable(using):
        # Bare decorator: @atomic
        # although the first argument is called `using`, it's actually the function being decorated.
        return AtomicWrapper(DEFAULT_DB_ALIAS, savepoint, isolation_level)(using)
    else:
        # Parametric decorator: @atomic(...) or context manager: with atomic(...): ...
        return AtomicWrapper(using, savepoint, isolation_level)


class AtomicWrapper(Atomic):
    _level_names = {
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT: 'AUTOCOMMIT',
        psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED: 'READ UNCOMMITTED',
        psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED: 'READ COMMITTED',
        psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ: 'REPEATABLE READ',
        psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE: 'SERIALIZABLE',
    }

    def __init__(self, using, savepoint, isolation_level):
        super(AtomicWrapper, self).__init__(using, savepoint)
        self.isolation_level = isolation_level
        self.isolation_level_name = AtomicWrapper._level_names[isolation_level]

    def __enter__(self):
        super(AtomicWrapper, self).__enter__()
        cursor = connection.cursor()
        cursor.execute('SET TRANSACTION ISOLATION LEVEL {}'.format(self.isolation_level_name))

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = super(AtomicWrapper, self).__exit__(exc_type, exc_val, exc_tb)
        if result:
            return result
        if exc_type == OperationalError:
            # Get exc_val.__cause__.pgcode
            pgcode = getattr(getattr(exc_val, '__cause__', None), 'pgcode', '')
            if pgcode == SERIALIZATION_FAILURE:
                raise ConcurrencyError()
        return result


class ConcurrencyError(Exception):
    pass
