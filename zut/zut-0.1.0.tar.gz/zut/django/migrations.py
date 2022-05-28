import logging, re
from pathlib import Path
from django.conf import settings
from django.db import migrations
from django.core.management import call_command

logger = logging.getLogger(__name__)

def get_runsql_operations(*paths):
    for path in paths:
        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            subpaths = sorted(path.iterdir())
            yield from get_runsql_operations(*subpaths)

        elif not path.name.endswith(".sql"):
            continue # ignore

        elif path.name.endswith("_revert.sql"):
            continue # ignore

        else:            
            reverse_path = path.parent.joinpath(path.name[:-4] + "_revert.sql")

            sql = path.read_text()
            reverse_sql = reverse_path.read_text() if reverse_path.exists() else None
            yield migrations.RunSQL(sql=sql, reverse_sql=reverse_sql)

_migration_name_re = re.compile(r"^(\d+)_")

def remake_migrations(after={}):
    # Rename manual migrations to py~
    for path in settings.BASE_DIR.glob("*/migrations/*_manual.py"):
        current = path.as_posix()
        if '.venv/' in current:
            continue
        target = f"{current}~"
        logger.info(f"rename {current} to {target}")
        path.rename(target)
    
    # Delete non-manual migrations
    for path in settings.BASE_DIR.glob("*/migrations/0*.py"):
        current = path.as_posix()
        if current.endswith("_manual.py") or '.venv/' in current:
            continue

        app_name = path.parent.parent.name
        if app_name in after:
            m = _migration_name_re.match(path.name)
            if m:
                migration_number = int(m.group(1))
                if migration_number >= after[app_name]:
                    logger.info(f"delete {current}")
                    path.unlink()
    
    logger.info("make migrations")
    call_command("makemigrations")

    # Rename manual migrations from py~
    for path in settings.BASE_DIR.glob("*/migrations/*_manual.py~"):
        current = path.as_posix()
        if '.venv/' in current:
            continue
        target = current[:-1]
        logger.info(f"rename {current} to {target}")
        path.rename(target)
