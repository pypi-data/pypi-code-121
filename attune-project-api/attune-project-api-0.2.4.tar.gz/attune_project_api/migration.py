import logging
import os
import sqlite3

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from attune_project_api import ObjectStorageContext


logger = logging.getLogger(__name__)


def runMigrationsForStorageContext(storageContext: ObjectStorageContext):
    currentRev = storageContext.getRevision()

    # Create a temporary database file
    db = sqlite3.connect("")
    cur = db.cursor()
    cur.execute("CREATE TABLE alembic_version(version_num varchar)")
    # What if someone sets currentRev to "Robert'); DROP TABLE users;--" ?
    cur.execute(
        f"INSERT INTO alembic_version (version_num) VALUES ('{currentRev}')"
    )
    db.commit()

    # Since sqlite3 can have only one memory DB per thread, this `:memory:` DB
    # will be the same as the one created previously
    engine = create_engine("sqlite:///")

    # Load the migration scripts and
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    latestRev = script.get_heads()[0]

    # The migration context expects a function to return an iterator of
    # revisions from a current revision (`revision`) to the destination
    # revision `latestRev`. The `script._upgrade_revs` method provides such
    # an iterator built from the scripts under `versions`
    def migrations_fn(revision, _ctx):
        return script._upgrade_revs(latestRev, revision)

    with engine.connect() as conn:
        context = MigrationContext.configure(
            connection=conn,
            opts={"transactional_ddl": False, "fn": migrations_fn},
        )

        if currentRev != latestRev:
            logger.info("Running migrations for Project API")
            context.run_migrations(storageContext=storageContext)
            storageContext.setRevision(latestRev)
            storageContext.squashAndMergeWorking(
                f"Migrate to {latestRev} revision"
            )


def getLatestRevision() -> str:
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    return script.get_heads()[0]
