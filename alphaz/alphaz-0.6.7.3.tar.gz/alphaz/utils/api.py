import copy
import traceback
import typing
from typing import List
from flask import (
    jsonify,
    make_response,
    request,
    send_file,
    send_from_directory,
    abort,
    url_for,
    render_template,
)

from ..models.main import AlphaException
from ..models.api import Parameter, ParameterMode, AlphaRequest
from ..models.api._route import Route
from ..models.tests._levels import Levels

from core import core

api = core.api
db = core.db
LOG = core.get_logger("api")

ROUTES = {}

# Specify the debug panels you want
# api.config['DEBUG_TB_PANELS'] = [ 'flask_debugtoolbar.panels.versions.VersionDebugPanel', 'flask_debugtoolbar.panels.timer.TimerDebugPanel', 'flask_debugtoolbar.panels.headers.HeaderDebugPanel', 'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel', 'flask_debugtoolbar.panels.template.TemplateDebugPanel', 'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel', 'flask_debugtoolbar.panels.logger.LoggingPanel', 'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel', 'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel' ]
# toolbar = flask_debugtoolbar.DebugToolbarExtension(api)

default_parameters = [
    Parameter("no_log", ptype=bool, private=True, cacheable=False, default=False),
    Parameter("reset_cache", ptype=bool, default=False, private=True, cacheable=False),
    Parameter("requester", ptype=str, private=True, cacheable=False),
    Parameter("format", ptype=str, default="json", private=True, cacheable=False),
    Parameter("admin", ptype=str, private=True, cacheable=False),
]
default_parameters_names = [p.name for p in default_parameters]


def _process_parameters(path: str, parameters: List[Parameter]) -> List[Parameter]:
    parameters = [] if parameters is None else parameters
    overrides = []
    for i, parameter in enumerate(parameters):
        if type(parameter) == str:
            parameter = Parameter(parameter)
            parameters[i] = parameter
        if parameter.name in default_parameters_names:
            if parameter.override:
                overrides.append(parameter.name)
                continue
            LOG.critical(
                f"Parameter could not be named <{parameter.name}> for route <{path}>!"
            )
            exit()

    output_parameter = [
        parameter for parameter in default_parameters if not parameter.name in overrides
    ]
    output_parameter.extend(parameters)
    return output_parameter


def route(
    path,
    parameters: typing.List[Parameter] = None,
    methods=["GET"],
    cache: bool = False,
    logged: bool = False,
    admin: bool = False,
    timeout: int = None,
    category: str = None,
    description: str = None,
    mode: str = None,
    route_log: bool = True,
    access_strings: typing.List[str] = [],
):
    path = "/" + path if path[0] != "/" else path

    parameters = _process_parameters(path, parameters)

    def api_in(func):
        api.add_url_rule(path, methods=methods, view_func=func, endpoint=func.__name__)

        @api.endpoint(func.__name__)
        def api_wrapper(*args, **kwargs):
            uuid_request = AlphaRequest.get_uuid()  # ";".join(methods) + '_' +
            __route = Route(
                uuid_request,
                path,
                parameters,
                request_state=request,
                cache=cache,
                timeout=timeout,
                admin=admin,
                logged=logged,
                cache_dir=api.cache_dir,
                log=api.log,
                description=description,
                jwt_secret_key=""
                if not "JWT_SECRET_KEY" in api.config
                else api.config["JWT_SECRET_KEY"],
                mode=mode,
            )
            api.routes_objects[uuid_request] = __route
            api.routes_objects = {
                x: y for x, y in api.routes_objects.items() if not y.is_outdated()
            }
            requester = __route.get("requester")
            if route_log:
                requester_head = f"{requester}: " if requester is not None else ""
                LOG.info(
                    f"{requester_head}Get api route {path} with function <{func.__name__}> and methods {','.join(methods)}"
                )

            if __route.ex is not None:
                LOG.error(ex=__route.ex)
                return __route.get_return()

            # check permissions
            if logged:
                token = AlphaRequest.get_token()
                user = api.get_logged_user()

                if logged and token is None:
                    error_msg = "Wrong permission: empty token"
                    if not __route.no_log:
                        LOG.warning(error_msg)
                    # __route.set_error_not_logged()
                    # return __route.get_return()
                    abort(make_response(jsonify(message=error_msg, error=True), 401))
                elif logged and (user is None or len(user) == 0):
                    error_msg = f"Wrong permission: {user=} not logged"
                    if not __route.no_log:
                        LOG.warning(error_msg)
                    # __route.set_error_not_logged()
                    # return __route.get_return()
                    abort(make_response(jsonify(message=error_msg), 401))
                if len(access_strings) != 0:
                    is_valid_access = any(
                        [x in user["user_roles"] for x in access_strings]
                    )
                    if not is_valid_access:
                        __route.access_denied()
                        return __route.get_return()
            if admin and not api.check_is_admin():
                __route.access_denied()
                return __route.get_return()

            """data = api.get_current_route().get_return()
            api.delete_current_route()
            return  __route.get_return()"""

            cached = __route.keep()
            if cached:
                cached = __route.get_cached()

            if not cached:
                try:
                    output = func(*args, **kwargs)
                    if output == "timeout":
                        __route.timeout()
                    elif output is not None:
                        __route.set_data(output)
                except Exception as ex:
                    if (
                        api.get("error_format")
                        and api.get("error_format").lower() == "exception"
                    ):
                        raise __route.set_error(ex)
                    if not "alpha" in str(type(ex)).lower():
                        if not __route.no_log:
                            LOG.error(ex)
                        __route.set_error(AlphaException(ex))
                    else:
                        __route.set_error(ex)
                if __route.cache:
                    __route.set_cache()

            data = __route.get_return()
            # api.delete_current_route()
            return data

        api_wrapper.__name__ = func.__name__

        key_parameters = []
        for parameter in parameters:
            if parameter.name == "reset_cache" and cache:
                key_parameters.append(parameter)
            elif not parameter.private:
                key_parameters.append(parameter)

        locals_p = locals()
        if not "category" in locals_p or category is None:
            groups = func.__module__.split(".")
            current_category = groups[-1]
            if len(groups) >= 2 and groups[-2] != "routes":
                current_category = "/".join(groups[-2:])
        else:
            current_category = category.lower()

        kwargs_ = {
            "path": path,
            "parameters": key_parameters,
            "parameters_names": [x.name for x in key_parameters],
            "methods": methods,
            "cache": cache,
            "logged": logged,
            "admin": admin,
            "timeout": timeout,
            "category": current_category,
            "description": description,
        }
        api_wrapper._kwargs = kwargs_

        paths = [x for x in path.split("/") if x.strip() != ""]
        if len(paths) == 1:
            paths = ["root", paths[0]]

        arguments = {
            x: y if x != "parameters" else [j.__dict__ for j in y]
            for x, y in kwargs_.items()
        }
        for parameter in arguments["parameters"]:
            if hasattr(parameter["ptype"], "metadata"):
                if hasattr(parameter["ptype"], "type_sa_class_manager"):
                    parameter["attributes"] = parameter[
                        "ptype"
                    ].type_sa_class_manager.local_attrs

        trace = traceback.format_stack()

        ROUTES["/".join(methods) + ":" + path] = {
            "category": current_category,
            "name": func.__name__,
            "module": "",
            "paths": paths,
            "arguments": arguments,
        }

        return api_wrapper

    return api_in


##################################################################################################################
# BASE API FUNCTIONS
##################################################################################################################


@api.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Origin,Accept,X-Requested-With,Content-Type,Authorization",
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    # response.headers.set('Allow', 'GET, PUT, POST, DELETE, OPTIONS')
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
