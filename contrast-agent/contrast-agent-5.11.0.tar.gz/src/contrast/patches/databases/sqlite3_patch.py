# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import register_post_import_hook
import sys
from contrast.agent.policy import patch_manager
from contrast.patches.databases import dbapi2
from contrast.utils.decorators import fail_quietly

SQLITE3 = "sqlite3"
PYSQLITE2_DBAPI2 = "pysqlite2.dbapi2"
VENDOR = "SQLite3"


class Sqlite3Patcher(dbapi2.Dbapi2Patcher):
    @fail_quietly("failed to get database inventory information")
    def init_dbinfo(self, connection, connect_args, connect_kwargs):
        # sqlite does not use a server, so no need for host/port
        database = connect_kwargs.get("database") or (
            connect_args[0] if len(connect_args) > 0 else "unknown"
        )
        self.dbinfo["database"] = database


def instrument_sqlite3(sqlite3):
    dbapi2.instrument_adapter(
        sqlite3, VENDOR, Sqlite3Patcher, extra_cursors=[sqlite3.Cursor]
    )


def instrument_pysqlite2_dbapi2(pysqlite2_dbapi2):
    """Supports the older pysqlite module in Py2"""
    dbapi2.instrument_adapter(
        pysqlite2_dbapi2,
        VENDOR,
        Sqlite3Patcher,
        extra_cursors=[pysqlite2_dbapi2.Cursor],
    )


def register_patches():
    register_post_import_hook(instrument_sqlite3, SQLITE3)
    register_post_import_hook(instrument_pysqlite2_dbapi2, PYSQLITE2_DBAPI2)


def reverse_patches():
    sqlite3 = sys.modules.get(SQLITE3)
    if sqlite3:
        patch_manager.reverse_patches_by_owner(sqlite3)
        patch_manager.reverse_patches_by_owner(sqlite3.Cursor)
        patch_manager.reverse_patches_by_owner(sqlite3.Connection)

    psqlite = sys.modules.get(PYSQLITE2_DBAPI2)
    if psqlite:
        patch_manager.reverse_patches_by_owner(psqlite)
        patch_manager.reverse_patches_by_owner(psqlite.Cursor)
        patch_manager.reverse_patches_by_owner(psqlite.Connection)
