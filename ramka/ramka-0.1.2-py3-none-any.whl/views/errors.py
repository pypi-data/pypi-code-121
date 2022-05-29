import json

from ramka.response import Response


def _error_page(response: Response, error_code: int, message: str) -> None:
    """Helper function to send an error page to the client.

    It updates the response object with the error details.

    Arguments:
        response (Response): The response object to send the error page to.
        error_code (int): The error code to send to the client.
        message (str): The message to send to the client.
    """
    response.status_code = error_code
    response.content_type = "application/json"
    response.text = json.dumps({"error": message})


def http_404_not_found(_, response):
    """The default 404 handler.

    It sends a 404 error page to the client.
    """
    _error_page(response, 404, "Not found.")


def http_405_method_not_allowed(_, response):
    """The default handler for methods that have not been implemented."""
    _error_page(response, 405, "Method not allowed.")


def default_error_handler(_, response, error: Exception):
    """The default handler for all unhandled exceptions.

    It sends a 500 error page to the client as all unhandles exceptions are considered
    as server errors. Instead of sending a genetic 500 error page, it sends a JSON
    response with the error message.
    """
    _error_page(response, 500, str(error))


__all__ = ["default_error_handler", "http_404_not_found", "http_405_method_not_allowed"]
