import inspect, glob, os, importlib, datetime

from flask_admin.contrib.sqla import ModelView

from ..utils import *

from ..models.logger import AlphaLogger
from sqlalchemy.orm.attributes import InstrumentedAttribute

TABLES = {}


def add_to_tables(db, obj):
    from alphaz.models.database.models import AlphaTable

    is_class = inspect.isclass(obj)
    if not is_class:
        return

    alpha_model = issubclass(obj, AlphaTable)
    has_table = hasattr(obj, "__tablename__")
    if alpha_model and has_table:
        db_name = db.name
        table_name = obj.__tablename__.upper()
        TABLES[db_name]["tables"][table_name] = obj
        return True
    return False


def get_definitions_modules(
    modules_list: List[ModuleType], log: AlphaLogger
) -> List[ModuleType]:
    """[Get database table definitions from parent or children module list]

    Args:
        modules_list (List[ModuleType]): [parent or children module list]
        log (AlphaLogger): [description]

    Returns:
        List[ModuleType]: [description]
    """
    log.info("Start getting definition modules")
    main = None

    modules = []
    modules_db = {}

    loaded_modules = []
    # TODO replace ?
    for module_r in modules_list:
        module = (
            importlib.import_module(module_r) if type(module_r) == str else module_r
        )

        if not module:
            log.error(f"Cannot load module <{module_r}>")
            continue

        dir_ini = module.__file__ and "__init__.py" in module.__file__
        if dir_ini:
            module_path = module.__file__.replace("__init__", "*")

        dir_path = hasattr(module, "__path__") and module.__path__
        if dir_path and hasattr(module.__path__, "_path"):
            dir_path = module.__path__._path and len(module.__path__._path) != 0
            module_path = module.__path__._path[0] + os.sep + "*"
        elif dir_path:
            dir_path = len(module.__path__) != 0
            module_path = module.__path__[0] + os.sep + "*"

        if dir_ini or dir_path:
            sub_files = glob.glob(module_path) if dir_ini else glob.glob(module_path)

            names = [
                os.path.basename(x).replace(".py", "")
                for x in sub_files
                if not "__init__" in x and ".py" in x
            ]

            for sub_file_name in names:
                module_full_name = f"{module.__name__}.{sub_file_name}"
                if module_full_name in loaded_modules:
                    continue

                loaded_modules.append(module_full_name)
                try:
                    sub_module = importlib.import_module(module_full_name)
                except Exception as ex:
                    log.error(f"Cannot load module {module_full_name}", ex=ex)
                    continue

                if not "db" in sub_module.__dict__:
                    continue
                db = sub_module.__dict__["db"]

                modules_db[sub_module] = db
        else:
            elements = module.__dict__
            if "alphaz" in module_r and "core" in elements:
                db = elements["core"].db
            elif not "db" in elements:
                LOG.error(
                    f"Cannot initialise module <{module_r}>, <db> parameter is missing"
                )
                continue
            else:
                db = elements["db"]
            modules_db[module] = db

    for module, db in modules_db.items():
        if db.main and db.name != "main":
            main = db.name
        if not db.name in TABLES:
            tables = db.get_engine().table_names()
            TABLES[db.name] = {"db": db, "tables": {x.upper(): None for x in tables}}

        for name, obj in module.__dict__.items():
            if add_to_tables(db, obj):
                modules.append(module)

    if main and main in TABLES:
        if not "main" in TABLES:
            TABLES["main"] = TABLES[main]
        else:
            for table, obj in TABLES[main]["tables"].items():
                if not table in TABLES["main"]["tables"]:
                    TABLES["main"]["tables"][table] = obj

    log.info("END getting definition modules")
    return modules


class AlphaModelView(ModelView):
    column_display_pk = True


def load_views(log) -> List[ModelView]:
    """[Load view from tables definitions module]

    Args:
        module (ModuleType): [description]

    Returns:
        List[ModelView]: [description]
    """
    views = []

    for schema, cf in TABLES.items():
        db, tables = cf["db"], cf["tables"]

        for table_name, class_object in tables.items():
            if class_object is None:
                # log.error('Cannot get class for table <%s>'%table_name)
                continue

            attributes = [
                x
                for x, y in class_object.__dict__.items()
                if isinstance(y, InstrumentedAttribute)
            ]

            name = "%s:%s" % (schema, class_object.__tablename__)
            view = AlphaModelView(
                class_object,
                db.session,
                name=class_object.__tablename__,
                category=schema,
                endpoint=name,
            )

            view.column_list = attributes
            views.append(view)
    if len(views) != 0:
        log.info(f"Loaded {len(views)} views models")
    return views
