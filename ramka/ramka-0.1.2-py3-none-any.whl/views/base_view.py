from abc import ABC

from ramka.request import Request
from ramka.response import Response


class BaseView(ABC):  # pylint: disable=too-few-public-methods
    """Base class for all class-based views.

    A class-based view is a view that is defined by a class. It defines methods for all
    supported request methods.
    """

    def get(  # pylint: disable=no-self-use,unused-argument
        self, request: Request, response: Response, **kwargs
    ) -> None:
        """GET HTTP method handler.

        It should be overridden in subclasses to enable support for the GET HTTP method.

        Arguments:
            request (Request): The request.
            response (Response): The response.
            kwargs (dict): The route parameters.
        """
        raise NotImplementedError()

    def post(  # pylint: disable=no-self-use,unused-argument
        self, request: Request, response: Response, **kwargs
    ) -> None:
        """POST HTTP method handler.

        It should be overridden in subclasses to enable support for the POST HTTP
        method.

        Arguments:
            request (Request): The request.
            response (Response): The response.
            kwargs (dict): The route parameters.
        """
        raise NotImplementedError()

    def put(  # pylint: disable=no-self-use,unused-argument
        self, request: Request, response: Response, **kwargs
    ) -> None:
        """PUT HTTP method handler.

        It should be overridden in subclasses to enable support for the PUT HTTP method.

        Arguments:
            request (Request): The request.
            response (Response): The response.
            kwargs (dict): The route parameters.
        """
        raise NotImplementedError()

    def patch(  # pylint: disable=no-self-use,unused-argument
        self, request: Request, response: Response, **kwargs
    ) -> None:
        """PATCH HTTP method handler.

        It should be overridden in subclasses to enable support for the PATCH HTTP
        method.

        Arguments:
            request (Request): The request.
            response (Response): The response.
            kwargs (dict): The route parameters.
        """
        raise NotImplementedError()

    def delete(  # pylint: disable=no-self-use,unused-argument
        self, request: Request, response: Response, **kwargs
    ) -> None:
        """DELETE HTTP method handler.

        It should be overridden in subclasses to enable support for the DELETE HTTP
        method.

        Arguments:
            request (Request): The request.
            response (Response): The response.
            kwargs (dict): The route parameters.
        """
        raise NotImplementedError()


__all__ = ["BaseView"]
