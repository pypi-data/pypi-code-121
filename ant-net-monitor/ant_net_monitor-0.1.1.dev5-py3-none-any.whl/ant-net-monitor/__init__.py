import os
import threading
import time

from flask import Flask, jsonify
from flask_cors import CORS

from .cli import init_db_command
from .extensions import db
from .status import Status, get_last_status, save_status


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("backend.config")

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

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/status")
    def getStatus():
        return jsonify(get_last_status())

    CORS(app)

    register_extensions(app)
    add_command(app)

    set_status_thread(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)


def add_command(app):
    """Register Flask CLI commands."""
    app.cli.add_command(init_db_command)


# TODO 测试情况下的环境变量
def set_status_thread(app):
    """Register status thread."""

    def save_status_loop(app):
        with app.app_context():
            if app.config["APPLICATION_ENV"] == "dev":
                while True:
                    save_status(Status())
                    time.sleep(1)
            elif app.config["APPLICATION_ENV"] == "test":
                for i in range(3):
                    save_status(Status())
                    time.sleep(1)

    save_status_thread = threading.Thread(target=save_status_loop, args=(app,))
    save_status_thread.start()
