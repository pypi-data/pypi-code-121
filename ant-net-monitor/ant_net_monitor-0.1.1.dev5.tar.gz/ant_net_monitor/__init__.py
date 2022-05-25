import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import logging

from .threads import set_all_threads

from .cli import init_db, init_db_command
from .extensions import db
from .status import Status
from .blueprint.status_blueprint import status_bp
from .blueprint.alarm_blueprint import alarm_bp

from .alarm.alarm import Alarm

__version__ = "0.1.1dev5"


def create_app(*, ENABLE_SNMP=False):
    """create and configure the app"""
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="./dist/static",
        template_folder="./dist",
    )
    app.config.from_object("ant_net_monitor.config")

    try:
        gunicorn_error_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.INFO)
    except Exception as e:
        print(e)

    # if test_config is None:
    #   # load the instance config, if it exists, when not testing
    #   app.config.from_pyfile("config.py", silent=True)
    # else:
    #   # load the test config if passed in
    #   app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + app.instance_path + "/backend.sqlite"
    )

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 15}}

    @app.route("/favicon.png")
    def fav():
        return send_from_directory(os.path.join(app.root_path, "dist"), "favicon.png")

    @app.route("/", defaults={"path": ""})
    @app.route("/<string:path>")
    @app.route("/<path:path>")
    def catch_all(path):
        return render_template("index.html")

    @app.route("/api/version")
    def return_version():
        return __version__

    if app.config["ENV"] == "development":
        app.config["ENABLE_SNMP"] = False
    else:
        app.config["ENABLE_SNMP"] = ENABLE_SNMP

    app.logger.info("SNMP MODE:" + str(app.config["ENABLE_SNMP"]))

    CORS(app)
    register_extensions(app)

    Status.init_app(app)

    check_table_exist(app)

    app.register_blueprint(status_bp)
    app.register_blueprint(alarm_bp)

    add_command(app)

    if app.config["ENABLE_SNMP"]:
        # TODO 仅作测试
        Status.init_agent(app, "localhost", "antrol")
        Status.init_agent_list(app)
        Alarm.init_snmp_alarm(app)
    else:
        Alarm.init_alarm(app)

    set_all_threads(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)


def add_command(app):
    """Register Flask CLI commands."""
    app.cli.add_command(init_db_command)


def check_table_exist(app):
    """Check if `basic_status` table exists."""

    with app.app_context():
        engine = db.get_engine()
        insp = db.inspect(engine)
        if "basic_status" not in insp.get_table_names():
            init_db()
