from ...utils.api import route, Parameter

from ...libs import logs_lib, flask_lib, database_lib

from ...models.main import AlphaException

from core import core

api = core.api
db = core.db
log = core.get_logger("api")


@route("/database/tables", admin=True)
def liste_tables():
    return database_lib.get_databases_tables_dict(core)


@route(
    "/database/create",
    admin=True,
    parameters=[Parameter("schema", required=True), Parameter("table", required=True)],
)
def create_table():
    created = core.create_table(api.get("schema"), api.get("table"))
    if created:
        log.info(f"table {api.get('table')} created")
    else:
        log.error(f"table {api.get('table')} notcreated")
    return created


@route(
    "/database/drop",
    admin=True,
    parameters=[Parameter("schema", required=True), Parameter("table", required=True)],
)
def drop_table():
    dropped = core.drop_table(api.get("schema"), api.get("table"))
    if dropped:
        return "table %s dropped" % api.get("table")


@route(
    "/database/init",
    admin=True,
    parameters=[
        Parameter("database", required=True),
        Parameter("table", required=True),
        Parameter("drop", ptype=bool),
    ],
)
def init_database():
    log = core.get_logger("database")
    database_lib.init_databases(
        core, api.get("database"), api.get("table"), drop=api.get("drop"), log=log
    )


@route(
    "/database/init/all",
    admin=True,
    parameters=[Parameter("database", required=True), Parameter("drop", ptype=bool)],
)
def init_all_database():
    log = core.get_logger("database")

    databases = database_lib.get_databases_tables_dict(core)
    if not api.get("database") in databases:
        raise AlphaException(
            "missing_database", parameters={"database": api.get("database")}
        )

    for table in databases[api.get("database")]:
        database_lib.init_databases(
            core, api.get("database"), table, drop=api.get("drop"), log=log
        )


@route("database/blocking", admin=True)
def get_blocking_queries():
    return core.db.get_blocked_queries()


@route(
    "/table",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
        Parameter("order_by", ptype=str),
        Parameter("direction", ptype=str),
        Parameter("page_index", ptype=int, default=0),
        Parameter("page_size", ptype=int, default=100),
    ],
    logged=True,
)
def get_transactions_history():
    return database_lib.get_table_content(**api.get_parameters())


@route(
    "/table/columns",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
    ],
)
def get_table_columns():
    return database_lib.get_table_columns(**api.get_parameters())


@route(
    "/table/model",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
    ],
)
def get_table_model():
    return database_lib.get_table_model(**api.get_parameters())