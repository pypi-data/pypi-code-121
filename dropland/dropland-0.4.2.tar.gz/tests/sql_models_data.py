from dropland.storages.sql import USE_SQL

if USE_SQL:
    pass

USE_SQLA = True
USE_GINO = True

try:
    # noinspection PyUnresolvedReferences
    from dropland.storages.sql.backends.sqla import SqlaModel

except ImportError:
    USE_SQLA = False

try:
    # noinspection PyUnresolvedReferences
    from dropland.storages.sql.backends.gino import GinoModel

except ImportError:
    USE_GINO = False


if USE_SQL:
    from tests.conftest import sql_storage

    sqla_sqlite = sql_storage.create_engine('asqlite')
    sqla_pg = sql_storage.create_engine('apg')
    sqla_mysql = sql_storage.create_engine('ams')
    gino_pg = sql_storage.create_engine('apg-gino')
    gino_mysql = sql_storage.create_engine('ams-gino')
