from inspect import isclass
from typing import Any, Callable, Dict, List, Optional, Union

from ramka.views import BaseView


class Route:
    """Route representation.

    A single route defines a path (e.g. `/users/`) and a view (e.g. UserView).

    The path should always be absolute which means it should start with a forward slash.
    It can consist of multiple arguments (e.g. `/users/{id}/`) and needs to be unique.

    The view can be either a class (that inherits from `ramka.views.BaseView`)
    or a function that accepts two arguments: the request and the response. For
    function-based views, additional argument with all supported methods can be
    specified. By default, each view only supports GET requests. For class-based views,
    the view can have multiple methods (e.g. get, post, put, delete, etc.) and the
    handler will be selected based on the request method.

    Each argument can have a type specified. For example, path `/users/{id:d}/` means
    that the argument `id` should be a decimal number. For full list of supported types
    see https://github.com/r1chardj0n3s/parse#format-specification.

    Fields:
        path (str): The path.
        view (Union[BaseView, Callable]): The view that will handle the path.
        methods (Optional[List[str]]): The HTTP methods supported by the view.
    """

    def __init__(
        self,
        path: str,
        view: Union[BaseView, Callable],
        methods: Optional[List[str]] = None,
    ):
        self.path = path
        self.view = view
        self.methods = methods or ["get", "head", "options"]

    def get_handler(self, method: Optional[str] = "get") -> Callable:
        """Get handler for the given method.

        If the view is a class, the handler will be selected based on the request
        method. If the view is a function, the handler will be the view itself.

        Arguments:
            method (str): Optional, the request method.

        Returns:
            Callable: The handler.

        Raises:
            (ValueError): If the method is not supported.
            (AttributeError): If the view is not a class or a function.
        """
        method = (method or "get").lower()

        if isclass(self.view):
            handler = getattr(self.view(), method, None)
            if handler is None:
                raise NotImplementedError(f"Method {method} is not allowed.")

            return handler

        if callable(self.view):
            if method not in self.methods:
                raise NotImplementedError(f"Method {method} is not allowed.")

            return self.view

        raise AttributeError("View is not a class or a function.")

    def __str__(self) -> str:
        return f"{self.path} -> {self.view}"

    def __repr__(self) -> str:
        return f"{self.path} -> {self.view}"


class ResolvedRoute(Route):
    """Resolved route representation.

    A route defines a path (e.g. `/users/`) and a view (e.g. UserView).

    A resolved route is a route with parameters resolved. It's used to match a
    request to a view and to generate a response using the parameters.

    Fields:
        path (str): The path.
        view (Union[BaseView, Callable]): The view that will handle the path.
        methods (Optional[List[str]]): The HTTP methods supported by the view.
        params (Dict[str, Any]): Resolved parameters.
    """

    def __init__(
        self,
        path: str,
        view: Union[BaseView, Callable],
        methods: Optional[List[str]],
        params: Dict[str, Any],
    ):
        super().__init__(path, view, methods)
        self.params = params

    @staticmethod
    def from_route(route: Route, params: Dict[str, Any]) -> "ResolvedRoute":
        """Create a resolved route from a route and parameters.

        Arguments:
            route (Route): The route.
            params (Dict[str, Any]): The parameters.
        """
        return ResolvedRoute(route.path, route.view, route.methods, params)

    def __str__(self) -> str:
        params_str = "&".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.path} ? {params_str} -> {self.view}"

    def __repr__(self) -> str:
        return f"{self.path} ? {self.params} -> {self.view}"


__all__ = ["Route", "ResolvedRoute"]
