# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Database adapter patch for psycopg2.
This module's cursor doesn't have an `executescript` method.
"""

import os
from contrast.extern.wrapt import register_post_import_hook

from contrast.patches.databases import dbapi2
from contrast.utils.decorators import fail_quietly

PSYCOPG2 = "psycopg2"
VENDOR = "PostgreSQL"


class Psycopg2Patcher(dbapi2.Dbapi2Patcher):
    @fail_quietly("failed to get database inventory information")
    def init_dbinfo(self, connection, connect_args, connect_kwargs):
        """
        Record DB inventory for a Postgres connection.

        Here we make a good effort to find connection params. There are several ways
        that these can be set, in the following order of priority (using dbname as an
        example):
        - using the `connection_factory` kwarg
        - as a kwarg itself - `dbname` or the deprecated `database`
        - via the dbname parameter in the dsn string
        - with the PGDATABASE environment variable

        Newer versions of psycopg2 (v2.7, ~2017) support connection.get_dsn_parameters,
        which provides a dictionary of the parsed connection params - we're interested
        in `dbname`.

        For now, it's still possible for us to miss the dbname (i.e. an old version of
        psycopg2 using the dsn string only), but this is unlikely and it would only
        affect inventory.
        """
        dsn_params = getattr(connection, "get_dsn_parameters", lambda: {})()
        host = (
            dsn_params.get("host")
            or connect_kwargs.get("host")
            or os.environ.get("PGHOST", "unknown_host")
        )
        port = (
            dsn_params.get("port")
            or connect_kwargs.get("port")
            or os.environ.get("PGPORT", "unknown_port")
        )
        dbname = (
            dsn_params.get("dbname")
            or connect_kwargs.get("dbname")
            or connect_kwargs.get("database")
            or os.environ.get("PGDATABASE", "unknown_database")
        )
        self.dbinfo["host"] = host
        self.dbinfo["port"] = port
        self.dbinfo["database"] = dbname


def instrument_psycopg2(psycopg2):
    dbapi2.instrument_adapter(
        psycopg2, VENDOR, Psycopg2Patcher, extra_cursors=[psycopg2.extensions.cursor]
    )


def register_patches():
    register_post_import_hook(instrument_psycopg2, PSYCOPG2)
