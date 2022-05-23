import logging

from flask import Flask, abort, make_response, Response
import flask_login  # type: ignore

from functools import wraps

from typing import Callable, Any


from JuMonC import settings
from JuMonC.helpers.generateToken import generateToken


logger = logging.getLogger(__name__)

RESTAPI = Flask("JuMonC.handlers")
RESTAPI.config['JSON_SORT_KEYS'] = False
RESTAPI.url_map.strict_slashes = False



RESTAPI.config['SECRET_KEY'] = generateToken()
login_manager = flask_login.LoginManager()
login_manager.init_app(RESTAPI)


if settings.ONLY_CHOOSEN_REST_API_VERSION:
    start_version = settings.REST_API_VERSION
else:
    start_version = 1
end_version = settings.REST_API_VERSION

api_version_path = "/v<int:version>"


def check_version(func: Callable[..., Response] ) -> Callable[..., Response]:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any) -> Response:
        if kwargs["version"] >= start_version and kwargs["version"] <= end_version:
            return func(*args, **kwargs)
        abort(404)
        return make_response("",404)
            
    return decorated_function