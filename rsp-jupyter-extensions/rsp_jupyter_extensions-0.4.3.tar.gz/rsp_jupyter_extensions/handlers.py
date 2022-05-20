"""
This is a Handler Module to facilitate our Jupyter extensions in the Rubin
Observatory Science Platform context.
"""
from notebook.utils import url_path_join as ujoin

from .environment import Environment_handler
from .execution import Execution_handler
from .hub import Hub_handler
from .query import Query_handler


def setup_handlers(web_app) -> None:
    """
    Function used to setup all the handlers used.
    """
    extmap = {
        r"/rubin/environment": Environment_handler,
        r"/rubin/execution": Execution_handler,
        r"/rubin/hub": Hub_handler,
        r"/rubin/query": Query_handler,
    }

    # add the baseurl to our paths...
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    # And now add the handlers.
    handlers = []
    for path in extmap:
        handlers.append((ujoin(base_url, path), extmap[path]))
    web_app.add_handlers(host_pattern, handlers)
