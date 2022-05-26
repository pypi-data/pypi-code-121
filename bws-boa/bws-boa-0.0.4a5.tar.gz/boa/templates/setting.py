template = """\
# generado automaticamente
import sys
import os
import logging


logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARN,
    format='[%(levelname).1s %(asctime).19s] %(message)s',
    datefmt='%y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_script import Manager, Command
from flask import Flask, Blueprint, url_for, jsonify
from flask import current_app as app
from flask.cli import AppGroup
from boa.admin.json import JSONEncoderCurstom
from boa.admin import create_admin
from boa.admin.bootstrap import bootstrap

admin = create_admin()
db = SQLAlchemy()
api = Blueprint('api', __name__, url_prefix="/api")
cmd = AppGroup("cmd", short_help="Commands of apps")
migrate = Migrate()

config_file = os.getenv('APP_CONFIG_FILE', "config.py")


def create_app(config=config_file):
    _app = Flask(__name__, static_folder="../static")
    _app.config.from_pyfile(config)
    _app.json_encoder = JSONEncoderCurstom
    
    exts = [
        admin, db, cmd
    ]
    migrate.init_app(_app, db)

    for ext in exts:
        if callable(getattr(ext, "init_app", None)):
            ext.init_app(_app)

    @_app.before_first_request
    def register_frontends():
        admin.bootstrap_frontends()
        
    with _app.app_context():
        _app.cli.add_command(cmd)
        bootstrap(_app, admin, ["config", "view", "routes", "models"])
        if "cmd" in sys.argv:
            bootstrap(_app, None, ["cmd"])
        _app.register_blueprint(api)

    return _app

"""