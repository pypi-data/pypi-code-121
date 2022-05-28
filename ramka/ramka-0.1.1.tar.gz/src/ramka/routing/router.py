from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union

from parse import parse

from ramka.routing.route import ResolvedRoute, Route
from ramka.views import BaseView


class BaseRouter(ABC):
    """Base router class.

    The responsibility of the routes is to know how to handle given request.

    Router, on the other hand, is responsible for storing all routes that have been
    defined in the application and finding correct routes for the requests.

    There are two ways to add a new route to the router: by using the `add_route` method
    or by using the `route` decorator. It is the case to allow developers adding routes
    in a preffered way.

    Fields:
        routes (List[Route]): The list of routes that have been defined in the
            application.
    """

    def __init__(self) -> None:
        self.routes: List[Route] = []

    @abstractmethod
    def add_route(
        self,
        path: str,
        view: Union[BaseView, Callable],
        methods: Optional[List[str]] = None,
    ) -> None:
        """Add a route to the router.

        It's supposed to be used as a method.

        Arguments:
            path (str): The path to add the route to.
            view (Union[BaseView, Callable]): The view to add the route to.
            methods (Optional[List[str]]): The list of methods to add the route to.
        """

    @abstractmethod
    def route(self, path: str) -> Callable:
        """Add a route to the router.

        It's supposed to be used as a decorator.

        Arguments:
            path (str): The path to add the route to.
        """

    @abstractmethod
    def resolve(self, path: str) -> ResolvedRoute:
        """Resolve the route for the given path.

        Arguments:
            path (str): The path to resolve the route for.

        Returns:
            ResolvedRoute: The resolved route.
        """

    @abstractmethod
    def has_route(self, path: str) -> bool:
        """Check if the router has a route for the given path.

        Arguments:
            path (str): The path to check.

        Returns:
            bool: True if the router has a route for the given path, False otherwise.
        """


class SimpleRouter(BaseRouter):
    """Simple router class.

    The responsibility of the routes is to know how to handle given request.

    Router, on the other hand, is responsible for storing all routes that have been
    defined in the application and finding correct routes for the requests.

    This router can resolve routes with or without trailing slashes (that behavior can
    be disabled).

    Fields:
        routes (List[Route]): The list of routes that have been defined in the
            application.
    """

    def __init__(self, force_trailing_slashes: bool = True):
        super().__init__()
        self._force_trailing_slashes = force_trailing_slashes

    def _handle_trailing_slashes(self, path: str) -> str:
        """Handle trailing slashes.

        If the router is configured to force trailing slashes, the path is updated to
        have trailing slash even if it doesn't have one.

        Otherwise, the path is returned as is.

        Arguments:
            path (str): The path to handle.

        Returns:
            str: The path with trailing slash added if necessary.
        """
        if self._force_trailing_slashes and not path.endswith("/"):
            return f"{path}/"

        return path

    def resolve(self, path: str) -> ResolvedRoute:
        """Resolve the route for the given path.

        Arguments:
            path (str): The path to resolve the route for.

        Returns:
            ResolvedRoute: The resolved route.
        """
        path = self._handle_trailing_slashes(path)
        for route in self.routes:
            parsed_path = parse(route.path, path)
            if parsed_path:
                return ResolvedRoute.from_route(route, parsed_path.named)

        return None

    def has_route(self, path: str) -> bool:
        """Check if the router has a route for the given path.

        Arguments:
            path (str): The path to check.

        Returns:
            bool: True if the router has a route for the given path, False otherwise.
        """
        return self.resolve(path) is not None

    def add_route(
        self,
        path: str,
        view: Union[BaseView, Callable],
        methods: Optional[List[str]] = None,
    ) -> None:
        """Add a route to the router.

        It's supposed to be used as a method.

        Arguments:
            path (str): The path to add the route to.
            view (Union[BaseView, Callable]): The view to add the route to.
            methods (Optional[List[str]]): The list of methods to add the route to.
        """
        if self.has_route(path):
            raise AttributeError("Route already exists.")

        self.routes.append(Route(self._handle_trailing_slashes(path), view, methods))

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable:
        """Add a route to the router.

        It's supposed to be used as a decorator.

        Arguments:
            path (str): The path to add the route to.
            methods (Optional[List[str]]): The list of methods to add the route to.

        Returns:
            Callable: The decorated function.
        """

        def wrapper(view: Union[BaseView, Callable]):
            self.add_route(path, view, methods)
            return view

        return wrapper


__all__ = ["BaseRouter", "SimpleRouter"]
