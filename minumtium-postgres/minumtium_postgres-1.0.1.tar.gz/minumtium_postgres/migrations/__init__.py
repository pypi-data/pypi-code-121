from __future__ import annotations

from typing import List

from sqlalchemy import text, inspect

from .versions import *
from .versions.version_0 import MIGRATION_TABLE_NAME


def has_version_table(engine):
    return inspect(engine).has_table(MIGRATION_TABLE_NAME)


def get_database_version(engine):
    with engine.connect() as connection:
        with connection.begin():
            result = connection.execute(
                text(f"SELECT version from {MIGRATION_TABLE_NAME}")).mappings().first()
            return int(result['version'])


def run_migrations(migrations, engine, schema):
    for migration in migrations:
        migration.do(engine, schema)


def update_database_version(engine, version: int):
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text(f"DELETE from {MIGRATION_TABLE_NAME}"))
            connection.execute(text(f"INSERT INTO {MIGRATION_TABLE_NAME} VALUES(:version)"), {'version': version})


def apply_migrations(engine, schema=None, migrations: List[MigrationVersion] = None):
    if not migrations:
        migrations = [Migration() for Migration in get_versions()]

    if not migrations:
        return

    migrations = sorted(migrations)

    if not has_version_table(engine):
        run_migrations(migrations, engine, schema)
        update_database_version(engine, migrations[-1].get_version())
        return

    version = get_database_version(engine)
    to_run = migrations[version + 1:]
    if to_run:
        run_migrations(to_run, engine, schema)
        update_database_version(engine, to_run[-1].get_version())
