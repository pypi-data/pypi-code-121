from typing import Any, Callable, Dict, List, Optional, Type, Union

from ramka.middleware import Middleware
from ramka.request import Request
from ramka.response import Response
from ramka.routing import BaseRouter, SimpleRouter
from ramka.static import BaseStaticFilesEngine, WhiteNoiseEngine
from ramka.templates import BaseTemplateEngine, JinjaTemplateEngine
from ramka.views import (
    BaseView,
    default_error_handler,
    http_404_not_found,
    http_405_method_not_allowed,
)


class App:
    """The main application class.

    This is the entrypoint for the application.
    """

    def __init__(
        self,
        root_dir: str,
        *,
        router: Optional[BaseRouter] = None,
        router_kwargs: Optional[Dict] = None,
        template_engine: Optional[BaseTemplateEngine] = None,
        template_engine_kwargs: Optional[Dict] = None,
        static_files_dir: Optional[str] = None,
        static_files_engine: Optional[BaseStaticFilesEngine] = None,
        static_files_engine_kwargs: Optional[Dict] = None,
        http_404_not_found_handler: Optional[Callable] = None,
        http_405_method_not_allowed_handler: Optional[Callable] = None,
        error_handler: Optional[Callable] = None,
        middleware_classes: Optional[List[Type[Middleware]]] = None,
    ):
        """Initialize the application.

        Arguments:
            root_dir (str): The root directory of the application.
            router (Optional[BaseRouter]): The router to use.
            router_kwargs (Optional[Dict]): The kwargs to pass to the router.
            template_engine (Optional[BaseTemplateEngine]): The template engine to use.
            template_engine_kwargs (Optional[Dict]): The kwargs to pass to the template
                engine.
            static_files_dir (Optional[str]): The directory containing static files.
            static_files_engine (Optional[BaseStaticFilesEngine]): The static files
                engine to use.
            static_files_engine_kwargs (Optional[Dict]): The kwargs to pass to the
                static files engine.
            http_404_not_found_handler (Optional[Callable]): The handler to use for
                HTTP 404 error (Not found).
            http_405_method_not_allowed_handler (Optional[Callable]): The handler to use
                for HTTP 405 error (Method not allowed).
            error_handler (Optional[Callable]): The handler to use for errors.
            middleware_classes (Optional[List[Type[Middleware]]]): The list of
                middleware classes to use.

        """
        self._router = router or SimpleRouter(**(router_kwargs or {}))
        self._template_engine = self._initialize_template_engine(
            root_dir, template_engine, template_engine_kwargs
        )
        self._static_files_engine = self._initialize_static_files_engine(
            static_files_dir, static_files_engine, static_files_engine_kwargs
        )
        self._middleware = self._initialize_middleware(middleware_classes)

        self._http_404_handler = http_404_not_found_handler or http_404_not_found
        self._http_405_handler = (
            http_405_method_not_allowed_handler or http_405_method_not_allowed
        )
        self._error_handler = error_handler or default_error_handler

    def __call__(self, environ, start_response):
        if self._static_files_engine:
            return self._static_files_engine(environ, start_response)

        return self._wsgi_app(environ, start_response)

    def _initialize_template_engine(  # pylint: disable=no-self-use
        self,
        root_dir: str,
        engine: Optional[BaseTemplateEngine] = None,
        arguments: Optional[Dict] = None,
    ) -> BaseTemplateEngine:
        """Initialize the template engine.

        Arguments:
            root_dir (str): The root directory of the application.
            engine (Optional[BaseTemplateEngine]): The engine to use.
            arguments (Optional[Dict]): The kwargs to pass to the engine.

        Returns:
            BaseTemplateEngine: The initialized template engine.
        """
        return engine or JinjaTemplateEngine(**(arguments or {"root_dir": root_dir}))

    def _initialize_static_files_engine(
        self,
        static_files_dir: str,
        engine: Optional[BaseStaticFilesEngine] = None,
        arguments: Optional[Dict] = None,
    ) -> BaseStaticFilesEngine:
        """Initialize the static files engine.

        Arguments:
            static_files_dir (str): The directory containing static files.
            engine (Optional[BaseStaticFilesEngine]): The engine to use.
            arguments (Optional[Dict]): The kwargs to pass to the engine.

        Returns:
            BaseStaticFilesEngine: The initialized static files engine.
        """
        if not static_files_dir:
            return None

        return engine or WhiteNoiseEngine(
            **(arguments or {"app": self._wsgi_app, "root_dir": static_files_dir})
        )

    def _initialize_middleware(
        self, middleware_classes: List[Type[Middleware]]
    ) -> Middleware:
        """Initialize the middleware.

        Arguments:
            middleware_classes (List[Type[Middleware]]): The list of middleware classes
                to use.

        Returns:
            Middleware: The initialized middleware.
        """
        middleware = Middleware(self)
        if middleware_classes:
            for middleware_class in middleware_classes:
                middleware.add(middleware_class)

        return middleware

    def _wsgi_app(self, environ, start_response):
        """The WSGI application.

        Arguments:
            environ (Dict): The WSGI environment.
            start_response (Callable): The WSGI start response function.

        Returns:
            The response body.
        """
        request = Request(environ)
        response = self._handle_request(request)
        return response(environ, start_response)

    def _handle_request(self, request: Request) -> Response:
        """Handle a request.

        Arguments:
            request (Request): The request to handle.

        Returns:
            Response: The response.

        Raises:
            Exception: An error occurred if no handler found.
        """
        response = Response()
        parsed_route = self._router.resolve(request.path)

        try:
            if parsed_route:
                handler = parsed_route.get_handler(request.method)
                handler(request, response, **parsed_route.params)
            else:
                self._http_404_handler(request, response)

        except NotImplementedError:
            self._http_405_handler(request, response)

        # Using `Exception` class as we want to catch all exception here.
        except Exception as error:  # pylint: disable=broad-except
            if self._error_handler is None:
                raise error

            self._error_handler(request, response, error)

        return response

    def has_route(self, path: str) -> bool:
        """Check if the router has a route for the given path.

        Arguments:
            path (str): The path to check.

        Returns:
            bool: True if the router has a route for the given path, False otherwise.
        """
        return self._router.has_route(path)

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
        self._router.add_route(path, view, methods)

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable:
        """Add a route to the router.

        It's supposed to be used as a decorator.

        Arguments:
            path (str): The path to add the route to.
            methods (Optional[List[str]]): The list of methods to add the route to.
        """
        return self._router.route(path, methods)

    def template(self, template_name, context: Dict[str, Any] = None) -> Any:
        """Render a template using defined template engine.

        Arguments:
            template_name (str): The name of the template to render.
            context (Optional[Dict[str, Any]]): The context to use.

        Returns:
            Any: The rendered template.
        """
        return self._template_engine.render(template_name, context)
