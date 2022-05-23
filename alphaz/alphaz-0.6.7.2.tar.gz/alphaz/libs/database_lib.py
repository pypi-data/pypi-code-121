import datetime, glob, os, importlib
from typing import Dict

from sqlalchemy import MetaData

from . import flask_lib, io_lib

from ..models.main import AlphaException


def convert_value(value):
    if type(value) == str and len(value) > 7 and value[4] == "/" and value[7] == "/":
        return datetime.datetime.strptime(value, "%Y/%m/%d")
    if value == "now()":
        return datetime.datetime.now()
    return value


def process_entries(db, table, log, values: list, headers: list = None):
    if headers is not None:
        headers = [
            x.lower().replace(" ", "_") if hasattr(x, "lower") else str(x).split(".")[1]
            for x in headers
        ]

        entries = [
            table(
                **{
                    headers[i]: convert_value(value)
                    for i, value in enumerate(values_list)
                }
            )
            for values_list in values
        ]
    else:
        entries = values

    # db.session.query(class_instance).delete()
    # db.session.add_all(entries)
    for entry in entries:
        db.session.merge(entry)

    db.session.commit()


def init_databases(core, database_name, table_name, drop=False, log=None):
    if len(flask_lib.TABLES) == 0:
        core.load_models_sources()
    """if core.configuration != 'local':
        if log: log.error('Configuration must be <local>')
        return"""

    database_names_in_lib = [x for x in flask_lib.TABLES if x.upper() == database_name.upper()]

    if not len(database_names_in_lib):
        raise AlphaException("cannot_find_schema", parameters={"schema": database_name})
        return False
    database_name_in_lib = database_names_in_lib[0]

    tablenames_in_lib = [ x for x in flask_lib.TABLES[database_name_in_lib]["tables"] if x.upper() == table_name.upper()]
    if not len(tablenames_in_lib):
        raise AlphaException("cannot_find_table", parameters={"table": table_name})
        return False
    tablename_in_lib = tablenames_in_lib[0]
    table = flask_lib.TABLES[database_name_in_lib]["tables"][tablename_in_lib]


    init_databases_config = core.config.get("databases")
    if init_databases_config is None:
        if log:
            log.error(
                "No initialisation configuration has been set in <databases> entry"
            )
        return False

    database_names_in_configs = [x for x in init_databases_config if x.upper() == database_name.upper()]
    if not len(database_names_in_configs):
        if log:
            log.error(
                "No initialisation configuration has been set in <databases> entry for database <%s>"
                % database_name
            )
        return False
    database_name_in_configs = database_names_in_configs[0]

    db = core.db

    if drop:
        if log:
            log.info("Drop table <%s> on <%s> database" % (table, database_name))
        db.metadata.drop_all(db.engine, tables=[table.__table__])

    db.metadata.create_all(db.engine, tables=[table.__table__])
    if log:
        log.info("Create table <%s> on <%s> database" % (table, database_name))
    db.commit()

    cf = init_databases_config[database_name_in_configs]
    if not len(cf):
        if log:
            log.error(
                "No initialisation configuration has been set in <databases> entry for database <%s>"
                % database_name
            )
        return False
        
    if type(cf) == str:
        cf = init_databases_config[cf]

    # json ini
    if "init_database_dir_json" in cf:
        json_ini = cf["init_database_dir_json"]
        files = glob.glob(json_ini + os.sep + "*.json")

        # if log: log.info('Initiating table %s from json files (%s): \n%s'%(database_name,json_ini,'\n'.join(['   - %s'%x for x in files])))
        for file_path in files:
            __process_databases_init(
                core, database_name, table_name, file_path, file_type="json", log=log
            )

    # python ini
    if "init_database_dir_py" in cf:
        py_ini = cf["init_database_dir_py"]
        files = [x for x in glob.glob(py_ini + os.sep + "*.py") if not "__init__" in x]

        # if log: log.info('Initiating table %s from python files (%s): \n%s'%(database_name,py_ini,'\n'.join(['   - %s'%x for x in files])))
        for file_path in files:
            __process_databases_init(
                core, database_name, table_name, file_path, log=log
            )

def __process_databases_init(
    core, database_name, table_name, file_path, file_type="py", log=None
):
    if file_type == "py":
        current_path = os.getcwd()
        module_path = (
            file_path.replace(current_path, "")
            .replace("/", ".")
            .replace("\\", ".")
            .replace(".py", "")
        )

        if module_path[0] == ".":
            module_path = module_path[1:]

        module = importlib.import_module(module_path)

        if hasattr(module, "ini"):
            ini = module.__dict__["ini"]
            if type(ini) != dict:
                if log:
                    log.error(
                        "In file %s <ini> configuration must be of type <dict>"
                        % (file_path)
                    )
                return

            __get_entries(core, database_name, table_name, file_path, ini, log=log)
    elif file_type == "json":
        try:
            ini = io_lib.read_json(file_path)
        except Exception as ex:
            if log:
                log.error("Cannot read file %s: %s" % (file_path, ex))
            return
        __get_entries(core, database_name, table_name, file_path, ini, log=log)


def __get_entries(core, database_name, table_name, file_path, configuration, log=None):
    # models_sources = [importlib.import_module(x) if type(x) == str else x for x in models_sources]
    for database, tables_config in configuration.items():
        db = database
        if type(database) == str:
            if database != database_name:
                continue

            db = core.db
            if db is None:
                if log:
                    log.error(
                        "In file %s configuration database <%s> is not recognized"
                        % (file_path, database)
                    )
                continue
        if db.name != database_name:
            continue

        if type(tables_config) != dict:
            if log:
                log.error(
                    "In file %s configuration of database <%s> must be of type <dict>"
                    % (file_path, database)
                )
            continue

        for table, config in tables_config.items():
            if table != table_name:
                continue

            found = False
            for schema, tables in flask_lib.TABLES.items():
                if table in tables["tables"]:
                    found = True
                    table = tables["tables"][table]

            if not found:
                if log:
                    log.error(
                        "In file %s configuration of database <%s> the table <%s> is not found"
                        % (file_path, database, table)
                    )
                continue

            if "headers" in config and "values" in config:
                if type(config["values"]) != list:
                    if log:
                        log.error(
                            'In file %s "values" key from table <%s> and database <%s> must be of type <list>'
                            % (file_path, table_name, database)
                        )
                    continue
                if type(config["headers"]) != list:
                    if log:
                        log.error(
                            'In file %s "headers" key from table <%s> and database <%s> must be of type <list>'
                            % (file_path, table_name, database)
                        )
                    continue

                headers_size = len(config["headers"])

                entries = []
                for entry in config["values"]:
                    if type(entry) != list:
                        if log:
                            log.error(
                                "In file %s from table <%s> and database <%s> entry <%s> must be of type <list>"
                                % (file_path, table_name, database, entry)
                            )
                        continue
                    entries.append(entry)

                if log:
                    log.info(
                        "Adding %s entries from <list> for table <%s> in database <%s> from file %s"
                        % (len(entries), table_name, database, file_path)
                    )
                process_entries(
                    db, table, log=log, headers=config["headers"], values=entries
                )

            if "objects" in config:
                entries = config["objects"]
                if log:
                    log.info(
                        "Adding %s entries from <objects> for table <%s> in database <%s> from file %s"
                        % (len(entries), table_name, database, file_path)
                    )
                process_entries(db, table, log=log, values=entries)


def get_databases_tables_dict(core) -> Dict[str, str]:
    return {} #TODO: update
    return {x: list(y.metadata.tables.keys()) for x, y in core.databases.items()}

def __get_table_model(schema: str, tablename: str):
    module = importlib.import_module(f"models.databases.{schema}")
    model = None
    for el in module.__dict__.values():
        if hasattr(el, "__tablename__") and el.__tablename__ == tablename:
            model = el
    if model is None:
        raise AlphaException(f"Cannot find {tablename=} in {schema=}")
    return model


def get_table_columns(schema: str, tablename: str):
    model = __get_table_model(schema, tablename)
    return model.get_columns()

def get_table_model(schema:str, tablename:str):
    model = __get_table_model(schema, tablename)
    return model.get_model()

def get_table_content(
    schema: str,
    tablename: str,
    order_by: str,
    direction: str,
    page_index: int,
    page_size: int,
):
    from core import core
    model = __get_table_model(schema, tablename)
    return core.db.select(
        model,
        page=page_index,
        per_page=page_size,
        order_by=order_by,
        order_by_direction=direction,
    )