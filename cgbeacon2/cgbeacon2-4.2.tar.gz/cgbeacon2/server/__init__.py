# -*- coding: utf-8 -*-
import logging
import os

from cgbeacon2.utils.notify import TlsSMTPHandler
from flask import Flask
from pymongo import MongoClient

from .blueprints import api_v1

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def configure_email_error_logging(app) -> None:
    """Setup logging of error/exceptions to email."""
    LOG.debug(f"Configuring email error logging to notify server admins:{app.config['ADMINS']}")

    mail_handler = TlsSMTPHandler(
        mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
        fromaddr=app.config["MAIL_USERNAME"],
        toaddrs=app.config["ADMINS"],
        subject=f"{app.name} - {app.config['DB_NAME']} - log error",
        credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(mail_handler)
    logging.getLogger("werkzeug").addHandler(mail_handler)


def create_app() -> Flask:
    """Method that creates the Flask app"""

    app = None
    app = Flask(__name__)

    try:
        app.config.from_envvar("CGBEACON2_CONFIG")
        LOG.info("Starting app envirironmental variable CGBEACON2_CONFIG")
    except RuntimeError:
        LOG.info(
            "CGBEACON2_CONFIG environment variable not found, configuring from default instance file."
        )
        app_root = os.path.abspath(__file__).split("cgbeacon2")[0]

        # check if config file exists under ../instance:
        instance_path = os.path.join(app_root, "cgbeacon2", "instance")
        if not os.path.isfile(os.path.join(instance_path, "config.py")):  # running app from tests
            instance_path = os.path.join(app_root, "cgbeacon2", "cgbeacon2", "instance")

        app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
        app.config.from_pyfile("config.py")

    if app.config.get("DB_URI") is None:
        LOG.warning("Please add database settings param in your config file.")
        quit()

    # If app is runned from inside a container, override host port
    db_uri = app.config["DB_URI"]

    client = MongoClient(db_uri)
    app.db = client[app.config["DB_NAME"]]
    LOG.info("database connection info:{}".format(app.db))

    app.register_blueprint(api_v1.api1_bp)

    # Configure email logging of errors
    if all(
        [
            app.config.get("ADMINS"),
            app.config.get("MAIL_SERVER"),
            app.config.get("MAIL_PORT"),
            app.config.get("MAIL_USERNAME"),
            app.config.get("MAIL_PASSWORD"),
        ]
    ):
        configure_email_error_logging(app)

    return app
