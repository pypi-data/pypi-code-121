from contextlib import contextmanager
from pathlib import Path
from typing import Optional
from click import secho

from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from macrostrat.utils import get_logger, relative_path
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert

from .utils import run_sql_file, run_query, get_or_create, run_sql_query_file
from .mapper import DatabaseMapper
from .postgresql import on_conflict, prefix_inserts


metadata = MetaData()

log = get_logger(__name__)


class Database(object):
    mapper: Optional[DatabaseMapper] = None
    __inspector__ = None

    def __init__(self, db_conn, app=None, echo_sql=False, **kwargs):
        """
        We can pass a connection string, a **Flask** application object
        with the appropriate configuration, or nothing, in which
        case we will try to infer the correct database from
        the SPARROW_BACKEND_CONFIG file, if available.
        """

        compiles(Insert, "postgresql")(prefix_inserts)

        log.info(f"Setting up database connection '{db_conn}'")
        self.engine = create_engine(
            db_conn, executemany_mode="batch", echo=echo_sql, **kwargs
        )
        metadata.create_all(bind=self.engine)
        self.meta = metadata

        # Scoped session for database
        # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
        # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
        self._session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self._session_factory)
        # Use the self.session_scope function to more explicitly manage sessions.

    def automap(self):
        log.info("Automapping the database")
        self.mapper = DatabaseMapper(self)
        self.mapper.automap_database()

    @contextmanager
    def session_scope(self, commit=True):
        """Provide a transactional scope around a series of operations."""
        # self.__old_session = self.session
        # session = self._session_factory()
        session = self.session
        try:
            yield session
            if commit:
                session.commit()
        except Exception as err:
            session.rollback()
            raise err
        finally:
            session.close()

    def _flush_nested_objects(self, session):
        """
        Flush objects remaining in a session (generally these are objects loaded
        during schema-based importing).
        """
        for object in session:
            try:
                session.flush(objects=[object])
                log.debug(f"Successfully flushed instance {object}")
            except IntegrityError as err:
                session.rollback()
                log.debug(err)

    def exec_sql_text(self, statement, *args, **kwargs):
        """
        Executes a sql command, in string on the database
        Easy way to load data into a test database instance
        """
        connection = self.engine.connect()
        connection.execute(text(statement), *args, **kwargs)

    def exec_sql(self, fn, params=None):
        """Executes SQL files passed"""
        # TODO: refactor this to exec_sql_file
        secho(Path(fn).name, fg="cyan", bold=True)
        run_sql_file(self.session, str(fn), params)

    def exec_sql_query(self, fn, params=None):
        return run_sql_query_file(self.session, fn, params)

    def exec_query(self, *args):
        """Returns a Pandas DataFrame from a SQL query"""
        return run_query(self.engine, *args)

    @property
    def inspector(self):
        if self.__inspector__ is None:
            self.__inspector__ = inspect(self.engine)
        return self.__inspector__

    def entity_names(self, **kwargs):
        """
        Returns an iterator of names of *schema objects*
        (both tables and views) from a the database.
        """
        yield from self.inspector.get_table_names(**kwargs)
        yield from self.inspector.get_view_names(**kwargs)

    def get(self, model, *args, **kwargs):
        if isinstance(model, str):
            model = getattr(self.model, model)
        return self.session.query(model).get(*args, **kwargs)

    def get_or_create(self, model, **kwargs):
        """
        Get an instance of a model, or create it if it doesn't
        exist.
        """
        if isinstance(model, str):
            model = getattr(self.model, model)
        return get_or_create(self.session, model, **kwargs)

    @property
    def table(self):
        """
        Map of all tables in the database as SQLAlchemy table objects
        """
        if self.mapper._tables is None:
            self.automap()
        return self.mapper._tables

    @property
    def model(self):
        """
        Map of all tables in the database as SQLAlchemy models

        https://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
        """
        if self.mapper._models is None:
            self.automap()
        return self.mapper._models

    @property
    def mapped_classes(self):
        return self.model
