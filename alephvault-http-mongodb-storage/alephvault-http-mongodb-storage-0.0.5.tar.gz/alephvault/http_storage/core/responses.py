from flask import jsonify, make_response


def auth_missing():
    return make_response(jsonify({"code": "authorization:missing-header"}), 401)


def auth_bad_schema():
    return make_response(jsonify({"code": "authorization:bad-scheme"}), 400)


def auth_syntax_error():
    return make_response(jsonify({"code": "authorization:syntax-error"}), 400)


def auth_not_found():
    return make_response(jsonify({"code": "authorization:not-found"}), 401)


def internal_error():
    return make_response(jsonify({"code": "internal-error"}), 500)


def not_found():
    return make_response(jsonify({"code": "not-found"}), 404)


def method_not_allowed():
    return make_response(jsonify({"code": "method-not-allowed"}), 405)


def ok(content=None):
    if content is None:
        content = {"code": "ok"}
    return make_response(jsonify(content), 200)


def created(id):
    return make_response(jsonify({"id": id}), 201)


def format_unexpected():
    return make_response(jsonify({"code": "format:unexpected"}), 400)


def format_invalid(errors):
    return make_response(jsonify({"code": "schema:invalid", "errors": errors}), 400)


def conflict_already_exists():
    return make_response(jsonify({"code": "already-exists"}), 409)


def conflict_duplicate_key(key_value):
    return make_response(jsonify({"code": "duplicate-key", "key": key_value}), 409)
