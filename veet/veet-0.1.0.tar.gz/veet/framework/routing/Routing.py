from types import FunctionType
from typing import Any
from fastapi.applications import FastAPI
from veet.core.logging import Log
from importlib import import_module


class Routing:

    app: FastAPI

    @classmethod
    def init(self, app):
        self.app = app

        return self

    def add_route(self, path: str, controller: Any, method: str = "GET", **kwargs):
        constroller = self._import_controller(controller)

        if constroller is not None:
            self.app.add_api_route(path=path, methods=[
                                   method], endpoint=constroller, **kwargs)

        return self

    def _import_controller(self, endpoint: Any):
        if isinstance(endpoint, FunctionType):
            return endpoint
        elif isinstance(endpoint, str):
            try:
                endpoints = endpoint.split("@")
                controller_dirs = endpoints[0].split("\\")
                controller_dirs_dot = ".".join(controller_dirs)
                controller_name = controller_dirs[-1]
                method_name = endpoints[-1]

                module = import_module(
                    f"app.controllers.{controller_dirs_dot}")
                controller = getattr(module, controller_name)

                return getattr(controller, method_name)
            except Exception as e:
                Log.error(f"Routing: {str(e)}")

                return None
        else:
            return None
