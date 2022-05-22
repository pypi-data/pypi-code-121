from jupyter_server.utils import url_path_join

from .transform_view import TransformJupyterRouteHandler
from .autocomplete_view import AutoCompleteRouteHandler
from .check_status_view import CheckStatusRouterHandler
from .file_action_view import FileActionRouterHandler

TRANSFORM_NB_ROUTE = "TRANSFORM_NB"
AUTOCOMPLETE_ROUTE = "AUTOCOMPLETE"
CHECK_STATUS = "CHECK_STATUS"
FILE_ACTION = "FILE_ACTION"


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    url_path = "jupyterlab-mutableai"

    autocomplete_route_pattern = url_path_join(
        base_url, url_path, AUTOCOMPLETE_ROUTE)

    transform_jupyter_route_pattern = url_path_join(
        base_url, url_path, TRANSFORM_NB_ROUTE
    )

    check_status_jupyter_route_pattern = url_path_join(
        base_url, url_path, CHECK_STATUS
    )

    file_action_jupyter_route_pattern = url_path_join(
        base_url, url_path, FILE_ACTION
    )

    handlers = [
        (autocomplete_route_pattern, AutoCompleteRouteHandler),
        (transform_jupyter_route_pattern, TransformJupyterRouteHandler),
        (check_status_jupyter_route_pattern, CheckStatusRouterHandler),
        (file_action_jupyter_route_pattern, FileActionRouterHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)
