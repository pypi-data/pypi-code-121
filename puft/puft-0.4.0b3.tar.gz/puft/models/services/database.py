import re
from functools import wraps
from typing import Callable

from warepy import log, format_message
from flask import Flask
import flask_migrate
from flask_sqlalchemy import SQLAlchemy

from .service import Service
from ...constants.enums import DatabaseTypeEnum


# Here database variable are referenced at top layer to be visible for ORMs.
# It is kinda messy, and in future it may be refactored (nothing more permanent than temporary).
native_db = SQLAlchemy()


# TODO: Fix type hinting for decorated functions under this decorator.
def migration_implemented(func: Callable):
    @wraps(func)
    def inner(self_instance, *args, **kwargs):
        if type(self_instance) is not Database:
            raise TypeError(
                format_message("Decorator migration_implemented cannot be applied to type {}.", type(self_instance))
            )
        elif not self_instance.migration:
            error_message = format_message("Migrate object hasn't been implemented yet.")
            raise AttributeError(error_message)
        else:
            return func(self_instance, *args, **kwargs)
    return inner


class Database(Service):
    """Operates over Database processes."""
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.DEFAULT_URI = f"sqlite:///{self.config['root_path']}/sqlite3.db"

        self.native_db = native_db
        # For now service config propagated to Database domain.
        self._assign_uri_from_config(config)

    @log.catch
    def _assign_uri_from_config(self, config: dict) -> None:
        raw_uri = config.get("uri", None)  # type: str

        if not raw_uri:
            raw_uri = self.DEFAULT_URI
            log.info(f"URI for database not specified, using default")
        else:
            # Case 1: SQLite database.
            # Developer can give relative path to the database (it will be absolutized at ConfigCell.parse()),
            # by setting sqlite database extension to `.db`, e.g. `./instance/sqlite3.db`,
            # or by setting full absolute path with protocol, e.g. `sqlite:////home/user/project/instance/sqlite3.db`.
            if raw_uri.rfind(".db") != -1 or "sqlite:///" in raw_uri:
                if "sqlite:///" not in raw_uri: 
                    # Set absolute path to db.
                    # Ref: https://stackoverflow.com/a/44687471/14748231
                    self.uri = "sqlite:///" + raw_uri
                else:
                    self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.SQLITE
            # Case 2: PostgreSQL database.
            elif re.match(r"postgresql(\+\w+)?://", raw_uri):
                # No need to calculate path since psql uri should be given in full form.
                self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.PSQL
            else:
                raise ValueError(format_message("Unrecognized or yet unsupported type of database uri: {}", raw_uri))
            
            # WARNING: Never print full database uri to config, since it may contain user's password (as in case of
            # psql)
            log.info(f"Set database type: {self.type_enum.value}")

    @log.catch
    @migration_implemented
    def init_migration(self, directory: str = "migrations", multidb: bool = False) -> None:
        """Initializes migration support for the application."""
        flask_migrate.init(directory=directory, multidb=multidb)

    @log.catch
    @migration_implemented
    def migrate_migration(
        self,
        directory: str = "migrations", 
        message = None, 
        sql = False, 
        head: str = "head", 
        splice = False, 
        branch_label = None, 
        version_path = None, 
        rev_id = None
    ) -> None:
        flask_migrate.migrate(
            directory=directory,
            message=message,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    @log.catch
    @migration_implemented
    def upgrade_migration(
        self,
        directory: str = "migrations",
        revision: str = "head",
        sql = False,
        tag = None
    ) -> None:
        flask_migrate.upgrade(
            directory=directory,
            revision=revision,
            sql=sql,
            tag=tag
        )

    @log.catch
    def setup(self, flask_app: Flask) -> None:
        """Setup database and migration object with given Flask app."""
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Supress warning.
        self.native_db.init_app(flask_app)

        # render_as_batch kwarg required only for sqlite3 databases to avoid ALTER TABLE issue on migrations
        # https://blog.miguelgrinberg.com/post/fixing-alter-table-errors-with-flask-migrate-and-sqlite
        if self.type_enum is DatabaseTypeEnum.SQLITE:
            is_sqlite_db = True
        else:
            is_sqlite_db = False
        self.migration = flask_migrate.Migrate(flask_app, self.native_db, render_as_batch=is_sqlite_db)

    @log.catch
    def get_native_db(self) -> SQLAlchemy:
        return self.native_db

    @log.catch
    @migration_implemented
    def get_migration(self) -> flask_migrate.Migrate:
        """Return migration object.
        
        Raise:
            AttributeError: If Migrate object hasn't implemented yet."""
        return self.migration

    @log.catch
    @migration_implemented
    def create_all_tables(self) -> None:
        self.native_db.create_all()

    @log.catch
    @migration_implemented
    def drop_all_tables(self):
        "Drop all tables."
        self.native_db.drop_all()

    @log.catch
    @migration_implemented
    def add_to_session(self, entity):
        """Place an object in the session."""
        # TODO: Add functionality to accept multiple entities as *args.
        self.native_db.session.add(entity)

    @log.catch
    @migration_implemented
    def commit_session(self):
        """Commit current transaction."""
        self.native_db.session.commit()

    @log.catch
    @migration_implemented
    def rollback_session(self):
        self.native_db.session.rollback()

    @log.catch
    @migration_implemented
    def remove_session(self):
        self.native_db.session.remove()
