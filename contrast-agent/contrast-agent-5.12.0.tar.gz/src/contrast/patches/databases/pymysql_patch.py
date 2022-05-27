# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import register_post_import_hook

from contrast.patches.databases import dbapi2

PYMYSQL = "pymysql"
VENDOR = "MySQL"


def instrument_pymysql(pymysql):
    dbapi2.instrument_adapter(
        pymysql, VENDOR, dbapi2.Dbapi2Patcher, extra_cursors=[pymysql.cursors.Cursor]
    )


def register_patches():
    register_post_import_hook(instrument_pymysql, PYMYSQL)
