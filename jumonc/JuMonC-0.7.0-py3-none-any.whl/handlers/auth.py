from typing import Dict, List, Union

from flask import jsonify, make_response, request, Response
from flask_login import login_user, login_required, current_user, logout_user  # type: ignore


from JuMonC.handlers.base import RESTAPI
from JuMonC.authentication import tokens, scopes, scope_name
from JuMonC.authentication.check import check_auth


@RESTAPI.route("/login", methods=["GET"])
def login() -> Response:
    token = request.args.get('token', default = None, type = str)
    scope = tokens.getTokenScope(token)
    if scope is None:
        return make_response(jsonify("The supplied token is not valid"), 400)
    
    login_user(scope)
    response_body = "Logged in with scope: " + scope_name[tokens.tokens[scope.id]]
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/scope", methods=["GET"])
@login_required
def scope() -> Response:
    response_body = "Scope: " + scope_name[tokens.tokens[current_user.id]]
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/logout", methods=["GET"])
@login_required
def logout() -> Response:
    response_body = "Logged out of scope: " + scope_name[tokens.tokens[current_user.id]]
    logout_user()
    return make_response(jsonify(response_body), 200)


def registerLogin() -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    return {
        "link": "/login",
        "isOptional": False,
        "description": "Calling this link allows you to login using the appropiate scope_token",
        "parameters": [
            {"name": "token",
             "description": "A token defining the access scope"}
        ]
    }
    
def registerLogout() -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    return {
        "link": "/logout",
        "isOptional": False,
        "description": "Calling this link removes the use of the scope token provided in the login function",
        "parameters": [
            {}
        ]
    }
    
def registerScope() -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    return {
        "link": "/scope",
        "isOptional": False,
        "description": "Calling this link shows the scope of this login",
        "parameters": [
            {}
        ]
    }


@RESTAPI.route("/test_auth_see_links", methods=["GET"])
@check_auth(scopes["see_links"])
def test_auth_see_links() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the see_links scope"
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/test_auth_retrieve_data", methods=["GET"])
@check_auth(scopes["retrieve_data"])
def test_auth_retrieve_data() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the retrieve_data scope"
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/test_auth_compute_data", methods=["GET"])
@check_auth(scopes["compute_data"])
def test_auth_compute_data() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the compute_data scope"
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/test_auth_retrieve_simulation_data", methods=["GET"])
@check_auth(scopes["retrieve_simulation_data"])
def test_auth_retrieve_simulation_data() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the retrieve_simulation_data scope"
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/test_auth_compute_simulation_data", methods=["GET"])
@check_auth(scopes["compute_simulation_data"])
def test_auth_compute_simulation_data() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the compute_simulation_data scope"
    return make_response(jsonify(response_body), 200)


@RESTAPI.route("/test_auth_full", methods=["GET"])
@check_auth(scopes["full"])
def test_auth_full() -> Response:
    response_body = "Your scope: " + scope_name[tokens.tokens[current_user.id]] + " gives authorisation to visit the full scope"
    return make_response(jsonify(response_body), 200)