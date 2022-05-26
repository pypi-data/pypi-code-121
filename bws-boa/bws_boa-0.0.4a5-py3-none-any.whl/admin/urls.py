import json
import gzip
from flask import make_response, jsonify, Response
from functools import wraps
from flask_admin import expose
from .json import JSONEncoderCurstom
from flask import request


def json_render(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        body = f(*args, **kwargs)
        try:
            if not isinstance(body, Response):
                if "gzip" in request.headers.get("Accept-Encoding", "") and not "json-not-gzip" in request.args:
                    content = gzip.compress(json.dumps(
                        body, cls=JSONEncoderCurstom).encode('utf8'), 5)
                    response = make_response(content)
                    response.headers['Content-length'] = len(content)
                    response.headers['Content-Encoding'] = 'gzip'
                    response.headers['Content-Type'] = 'application/json'
                    return response
                else:
                    return jsonify(body)
            return body
        except Exception as e:
            return body

    return decorated_view


def expose_json(url='/', methods=('GET',)):
    """
        Use este decorador para responder json
    """
    def wrap(f):
        if not hasattr(f, '_urls'):
            f._urls = []
        f._urls.append((url, methods))

        return json_render(f)
    return wrap


__all__ = [
    "expose",
    "json_render",
    "expose_json" ,  
]
