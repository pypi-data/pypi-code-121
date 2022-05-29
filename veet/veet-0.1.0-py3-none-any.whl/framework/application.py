from fastapi import FastAPI
from .routing.Routing import Routing
from ..core import paths
from .. import __version__, config
from importlib import import_module
import fnc
import os


class Application(FastAPI):

    db = None
    db_client = None

    def bootstrap(self):
        self.title = fnc.get("docs.title", config, default="Veet")
        self.version = fnc.get("docs.version", config, default=__version__)

        self.routing()

        return self

    def routing(self):
        Routing.init(self)

        self.dynamic_routing()

    def dynamic_routing(self):
        if os.path.isdir(paths.ROUTES_PATH):
            for module in paths.list_dir(paths.ROUTES_PATH):
                import_module(f"routes.{module}")
