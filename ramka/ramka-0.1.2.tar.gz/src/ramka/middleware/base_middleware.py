from typing import TYPE_CHECKING, Type

from ramka.request import Request
from ramka.response import Response

if TYPE_CHECKING:
    from ramka.app import App


class Middleware:
    """Base middleware class.

    Middleware is a class that can be used to modify the request and response objects.
    The idea is that middleware wraps the application and it can be wrapped with another
    middleware. This way, the application can be easily extended. For example,
    a middleware can be used to log the requests, and another middleware can be used
    to add some header to the response.

    Subclass this class and override the `process_request` and `process_response`
    methods to implement custom middleware. Each middleware can override one of those
    methods or both.
    """

    def __init__(self, app: "App") -> None:
        """Initialize the middleware.

        Arguments:
            app (App): The application to wrap.
        """
        self._app = app

    def __call__(self, environ, start_response) -> Response:
        request = Request(environ)
        response = self._app.handle_request(request)

        return response(environ, start_response)

    def add(self, middleware_cls: Type["Middleware"]):
        """Add another middleware to the execution chain.

        Arguments:
            middleware_cls (Type[Middleware]): The middleware class to add.
        """
        self._app = middleware_cls(self._app)

    def handle_request(self, request: Request) -> Response:
        """Handle the request.

        This method is called by the application. It calls the `process_request`
        method before the request is handled, and then the `process_response` method
        after the request is handled.

        Arguments:
            request (Request): The request to handle.
        """
        self.process_request(request)
        response = self._app.handle_request(request)
        self.process_response(request, response)

        return response

    def process_request(self, request: Request) -> None:  # pylint: disable=no-self-use
        """Process the request.

        This method is called by the application before the request is handled. It
        can be overridden to add custom logic to the request.

        Arguments:
            request (Request): The request to process.
        """

    def process_response(  # pylint: disable=no-self-use
        self, request: Request, response: Response
    ) -> None:
        """Process the response.

        This method is called by the application after the request is handled. It
        can be overridden to add custom logic to the response. It takes the request
        as one of the arguments but modifying it won't have any effect as the request
        is already handled.

        Arguments:
            request (Request): The request object.
            response (Response): The response to process.
        """
