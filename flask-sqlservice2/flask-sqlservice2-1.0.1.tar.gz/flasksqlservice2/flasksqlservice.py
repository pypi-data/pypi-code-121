from typing import Optional, TYPE_CHECKING
from flask import g

from sqlservice import Database, Session, ModelBase
if TYPE_CHECKING:
    from flask import Flask
from werkzeug.utils import import_string

from flask import g
from flask.cli import with_appcontext, AppGroup


class FlaskSQLService(object):

    """Flask extension for sqlservice.Database instance
    Main aim is to provide:
    - Flak extension style object for `sqlservice.Database`
    - Use `flask.configs` to provide parameters of `sqlservice.Database`.
    - Create database `Session` for each request & close it properly after the request finished.
    - The database session is available as `flask.g.dbsession`
    """

    def __init__(
        self,
        app: Optional["Flask"] = None
    ):
        """
        __init__ FlaskSQLService initiator

        :param app: The flask app instance, defaults to None
        :type app: Flask, optional
        """
        if app:
            self.init_app(app)

    def init_app(self, app: "Flask"):
        """
        init_app init sqlservice database by the configs specified in the app

        If you pass `app` to the `FlaskSQLService` constructor, This method will be called
        from the constructor.
        If you pass `None` to the constructor, You should call this method in somewhere.

        :param app: The flask app instance
        :type app: Flask
        :raises ValueError: raised if `uri` parameter & `app.config[`SQL_DATABASE_URI`]` are None
        :return: None
        :rtype: None
        """
        options = self.extract_options(app)
        self.collect_all_models(app)
        database_class = app.config.get("DATABASE_CLASS", None) or Database
        self.db = database_class(**options)
        self._add_session_handlers(app, options.get(
            "autoflush", None), options.get("expire_on_commit", None),)
        self._add_commands(app, options.get("SQL_CLI_GROUP", "sql"))
        app.extensions[app.config.get("SQL_EXTENSION_KEY", "sql-db")] = self

    def extract_options(self, app: "Flask"):
        options = {}
        uri = app.config.get("SQL_DATABASE_URI")
        if not uri:
            raise ValueError("Database uri can't be `None`")
        options["uri"] = uri

        model_class = app.config.get(
            "SQL_MODEL_CLASS"
        )
        if not model_class:
            from .model import Model
            model_class = Model

        options["model_class"] = model_class
        options["session_class"] = app.config.get(
            "SQL_SESSION_CLASS", Session
        )
        options["session_options"] = app.config.get("SQL_SESSION_OPTIONS", {})
        options["engine_options"] = app.config.get("SQL_ENGINE_OPTIONS")

        options["autoflush"] = app.config.get("SQL_AUTOFLUSH")
        options["expire_on_commit"] = app.config.get("SQL_EXPIRE_ON_COMMIT")

        options["isolation_level"] = app.config.get("SQL_ISOLATION_LEVEL")
        options["pool_size"] = app.config.get("SQL_POOL_SIZE")
        options["pool_timeout"] = app.config.get("SQL_POOL_TIMEOUT")
        options["pool_recycle"] = app.config.get("SQL_POOL_RECYCLE")
        options["pool_pre_ping"] = app.config.get("SQL_POOL_PRE_PING")
        options["poolclass"] = app.config.get("SQL_POOL_CLASS")
        options["max_overflow"] = app.config.get("SQL_MAX_OVERFLOW")
        options["paramstyle"] = app.config.get("SQL_PARAM_STYLE")

        options["encoding"] = app.config.get("SQL_ENCODING")
        options["execution_options"] = app.config.get("SQL_EXECUTION_OPTIONS")

        options["echo"] = app.config.get("SQL_ECHO")
        options["echo_pool"] = app.config.get("SQL_ECHO_POOL")

        return options

    def collect_all_models(self, app):
        models = app.config.get("SQL_DATABASE_MODELS", [])
        for mod in models:
            if isinstance(mod, str):
                import_string(mod)

    def _add_session_handlers(self, app, autoflush=None, expire_on_commit=None):
        @app.before_request
        def create_dbsession():
            g.dbsession = self.db.session(
                autoflush=autoflush, expire_on_commit=expire_on_commit
            )

        # Ensure that the session is closed on app context teardown so we
        # don't leave any sessions open after the request ends.
        @app.after_request
        def shutdown_session(response_or_exc):
            g.dbsession.close()  # type: ignore
            return response_or_exc

    def _add_commands(self, app: "Flask", group_name: str):
        group = AppGroup(group_name)

        @group.command()
        @with_appcontext
        def create_all():
            self.collect_all_models(app)
            self.db.create_all()

        @group.command()
        @with_appcontext
        def drop_all():
            self.db.drop_all()

        app.cli.add_command(group)
