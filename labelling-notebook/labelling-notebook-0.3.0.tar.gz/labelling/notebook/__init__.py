import os

from flask import Flask, jsonify, redirect
from werkzeug.exceptions import HTTPException


def create_app(
        instance_path=None,
        static_folder='../frontend/build'
):
    app = Flask(__name__,
                instance_path=instance_path,
                static_url_path='/',
                static_folder=static_folder,
                instance_relative_config=True)

    # Apply API blueprints
    from labelling.notebook import api_files
    app.register_blueprint(api_files.bp)
    # app.register_blueprint(other_api.bp)

    @app.errorhandler(ValueError)
    def http_error_handler(error):
        return jsonify(code=400, message=str(error)), 400

    @app.errorhandler(HTTPException)
    def http_error_handler(error):
        return jsonify(code=error.code, message=error.description), error.code

    @app.route('/')
    def home():
        return redirect('/index.html', code=302)

    _init_temp_dir(app)
    return app


def _init_temp_dir(app):
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

