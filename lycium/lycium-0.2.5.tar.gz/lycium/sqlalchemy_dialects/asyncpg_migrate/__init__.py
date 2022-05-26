import re
import json as _py_json
import sqlalchemy.dialects.postgresql.base
import sqlalchemy.dialects.postgresql.asyncpg

def overwrite_base_pg_dialect_get_server_version_info(self, connection):
    v = connection.exec_driver_sql("select pg_catalog.version()").scalar()
    m = re.match(
        r".*(?:PostgreSQL|EnterpriseDB|CockroachDB CCL) "
        r"v?(\d+)\.?(\d+)?(?:\.(\d+))?(?:\.\d+)?(?:devel|beta)?",
        v,
    )
    if not m:
        raise AssertionError(
            "Could not determine version from string '%s'" % v
        )
    return tuple([int(x) for x in m.group(1, 2, 3) if x is not None])

sqlalchemy.dialects.postgresql.base.PGDialect._get_server_version_info = overwrite_base_pg_dialect_get_server_version_info

def overwrite_pg_dialect_asyncpg_on_connect(self):
    super_connect = super(sqlalchemy.dialects.postgresql.asyncpg.PGDialect_asyncpg, self).on_connect()

    def _jsonb_encoder(str_value):
        # \x01 is the prefix for jsonb used by PostgreSQL.
        # asyncpg requires it when format='binary'
        return b"\x01" + str_value.encode()

    deserializer = self._json_deserializer or _py_json.loads

    def _json_decoder(bin_value):
        return deserializer(bin_value.decode())

    def _jsonb_decoder(bin_value):
        # the byte is the \x01 prefix for jsonb used by PostgreSQL.
        # asyncpg returns it when format='binary'
        return deserializer(bin_value[1:].decode())

    async def _setup_type_codecs(db_name, db_major_ver, conn):
        """set up type decoders at the asyncpg level.

        these are set_type_codec() calls to normalize
        There was a tentative decoder for the "char" datatype here
        to have it return strings however this type is actually a binary
        type that other drivers are likely mis-interpreting.

        See https://github.com/MagicStack/asyncpg/issues/623 for reference
        on why it's set up this way.
        """
        # await conn._connection.set_type_codec(
        #     "json",
        #     encoder=str.encode,
        #     decoder=_json_decoder,
        #     schema="pg_catalog",
        #     format="binary",
        # )
        # await conn._connection.set_type_codec(
        #     "jsonb",
        #     encoder=_jsonb_encoder,
        #     decoder=_jsonb_decoder,
        #     schema="pg_catalog",
        #     format="binary",
        # )
        # CockroachDB only has `jsonb`
        if db_name != "CockroachDB CCL":
            await conn._connection.set_type_codec(
                "json",
                encoder=str.encode,
                decoder=_json_decoder,
                schema="pg_catalog",
                format="binary",
            )

        try:
            # This only works on DBs other than CockroachDB, other than
            # versions greater than 21.1.0. This check is good enough
            # because there also aren't any 21.0.* versions.
            jsonb_support = (
                db_name != "CockroachDB CCL"
                or (
                    db_name == "CockroachDB CCL"
                    and int(db_major_ver) > 21
                )
            )
        except ValueError:
            # Short-circuit evaluation means this will only happen if the
            # database is CockroachDB and the version is unparseable, in
            # which case it's probably safe to assume that jsonb won't work
            jsonb_support = False

        if jsonb_support:
            await conn._connection.set_type_codec(
                "jsonb",
                encoder=_jsonb_encoder,
                decoder=_jsonb_decoder,
                schema="pg_catalog",
                format="binary",
            )

    def connect(conn):
        f = conn._connection.fetch("select version()")
        v = conn.await_(f)[0]["version"]
        m = re.match(
            r".*(PostgreSQL|EnterpriseDB|CockroachDB CCL) "
            r"v?(\d+)\.?(?:\d+)?(?:\.(?:\d+))?(?:\.\d+)?(?:devel|beta)?",
            v
        )
        if not m:
            raise AssertionError(
                "Could not determine database kind from string '%s'" % v
            )

        conn.await_(_setup_type_codecs(m.group(1), m.group(2), conn))
        if super_connect is not None:
            super_connect(conn)

    return connect

sqlalchemy.dialects.postgresql.asyncpg.PGDialect_asyncpg.on_connect = overwrite_pg_dialect_asyncpg_on_connect
