from typing import Any
from .Routing import Routing

routing = Routing()


class Route:

    @classmethod
    def get(self, path, controller=None, **kwargs: Any):
        return routing.add_route(path=path, method="GET", controller=controller, **kwargs)

    @classmethod
    def post(self, path, controller=None, **kwargs: Any):
        return routing.add_route(path=path, method="POST", controller=controller, **kwargs)

    @classmethod
    def put(self, path, controller=None, **kwargs: Any):
        return routing.add_route(path=path, method="PUT", controller=controller, **kwargs)
