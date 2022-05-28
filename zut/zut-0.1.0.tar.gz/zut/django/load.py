import logging, csv
from pathlib import Path
from django.utils import timezone
from psycopg2.sql import SQL, Identifier
from django.db import connection
from ..text import safe_slugify

logger = logging.getLogger(__name__)

def copy_from_csv(path, model_cls, truncate = False, delimiter = ";", encoding = "utf-8", accept_ignored_headers = True, mapping = None, static_mapping = None):
    if not hasattr(model_cls, "objects") or not hasattr(model_cls.objects, "from_csv"):    
        raise ValueError("missing %s.objects.from_csv, did you specified `objects = CopyManager()`?" % model_cls.__qualname__)

    db_table = model_cls._meta.db_table
    logger.info("load %s in table %s (model %s)", path, db_table, model_cls.__name__)

    fields = [field.name for field in model_cls._meta.get_fields()]

    # Get CSV headers
    headers = []
    with open(path, newline="", encoding=encoding) as file:
            reader = csv.reader(file, delimiter=delimiter)
            for row in reader:
                headers = row
                break

    if not headers:
        raise ValueError("headers not found in %s", path)

    # Build mapping
    if mapping is None:
        mapping = {}
    ignored_headers = ""
    for name in headers:
        slug = safe_slugify(name, separator="_")

        if slug in mapping:
            if mapping[slug] != name:
                logger.warning("ignore header \"%s\" (slug \"%s\" already added mapped to header \"%s\")", name, slug, mapping[slug])
            continue 

        if slug in fields:
            mapping[slug] = name
            continue

        ignored_headers += (", " if ignored_headers else "") + name + (f" ({slug})" if slug != name else "")

    if ignored_headers:
        logger.log(logging.INFO if accept_ignored_headers else logging.WARNING, "headers ignored in %s: %s", path.name, ignored_headers)

    if static_mapping is None:
        static_mapping = {}
    if "load_at" in fields and not "load_at" in static_mapping:
        static_mapping["load_at"] = timezone.now()
   
    # Truncate table
    if truncate:
        logger.debug("truncate %s (%s)", db_table, model_cls.__name__)
        with connection.cursor() as cursor:
            cursor.execute(SQL("TRUNCATE TABLE {}").format(Identifier(db_table)))

    # Import
    insert_count = model_cls.objects.from_csv(path, mapping=mapping, static_mapping=static_mapping, delimiter=delimiter)
    logger.info("%d records loaded", insert_count)


def call_procedure(name):
    with connection.cursor() as cursor:
        logger.info("call %s", name)
        cursor.execute(SQL("call {}()").format(Identifier(name)))


def seed_sql(*paths):
    for path in paths:
        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            subpaths = sorted(path.iterdir())
            seed_sql(*subpaths)

        elif not path.name.endswith(".sql"):
            continue # ignore

        elif path.name.endswith("_revert.sql"):
            continue # ignore

        else:        
            logger.info("seed sql %s", path)
            sql = path.read_text()
            with connection.cursor() as cursor:
                cursor.execute(sql)


def seed_enum(model_class, value_field="id", name_field="name", attr_fields=None):
    if not hasattr(model_class, "Enum"):
        raise ValueError("model class %s has no Enum attribute" % model_class)
    enum_class = model_class.Enum

    for literal in enum_class:
        defaults = {
            name_field: literal.name
        }

        if attr_fields:
            for attr, field in attr_fields.items():
                defaults[field] = getattr(literal, attr)

        kwargs = {
            value_field: literal.value,
            "defaults": defaults
        }
        model_class.objects.update_or_create(**kwargs)
