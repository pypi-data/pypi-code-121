# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import register_post_import_hook

from contrast.patches.databases import dbapi2

MYSQL_CONNECTOR = "mysql.connector"
VENDOR = "MySQL"


def instrument_mysql_connector(mysql_connector):
    dbapi2.instrument_adapter(
        mysql_connector,
        VENDOR,
        dbapi2.Dbapi2Patcher,
        extra_cursors=[
            mysql_connector.cursor.CursorBase,
            mysql_connector.cursor.MySQLCursor,
            mysql_connector.cursor_cext.CMySQLCursor,
        ],
    )


def register_patches():
    register_post_import_hook(instrument_mysql_connector, MYSQL_CONNECTOR)
