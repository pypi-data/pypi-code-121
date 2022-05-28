from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from ramka.app import App
from ramka.response import Response


class TestSession(RequestsSession):
    """The test session class.

    The test session is a wrapper around the requests library. It provides helper
    methods to make testing more straightforward.
    """

    def __init__(self, base_url: str, adapter: RequestsWSGIAdapter):
        """Initialize the test session.

        Arguments:
            base_url (str): The base URL to use for the test session.
            adapter (WSGIAdapter): The adapter to use for the test session.
        """
        super().__init__()
        self._base_url = base_url
        self.mount(prefix=self._base_url, adapter=adapter)

    @property
    def base_url(self) -> str:
        """The base URL of the test session.

        Returns:
            str: The base URL of the test session.
        """
        return self._base_url.rstrip("/")

    def _request(self, method: str, url: str, **kwargs) -> Response:
        """The request method.

        It makes a request to the test session.

        Arguments:
            method (str): The request method.
            url (str): The URL to request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        func = getattr(super(), method)
        if not func:
            raise AttributeError(f"Method {method} not supported.")

        url = url.lstrip("/")
        return func(f"{self.base_url}/{url}", **kwargs)

    def get(self, url, **kwargs) -> Response:
        """Perform a GET request.

        Arguments:
            url (str): The URL to request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        return self._request("get", url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs) -> Response:
        """Perform a POST request.

        Arguments:
            url (str): The URL to request.
            data (Optional[Dict]): The data to send with the request.
            json (Optional[Dict]): The JSON to send with the request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        return self._request("post", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs) -> Response:
        """Perform a PUT request.

        Arguments:
            url (str): The URL to request.
            data (Optional[Dict]): The data to send with the request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        return self._request("put", url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs) -> Response:
        """Perform a PATCH request.

        Arguments:
            url (str): The URL to request.
            data (Optional[Dict]): The data to send with the request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        return self._request("patch", url, data=data, **kwargs)

    def delete(self, url, **kwargs) -> Response:
        """Perform a DELETE request.

        Arguments:
            url (str): The URL to request.
            kwargs (Dict): The keyword arguments to pass to the request method.

        Returns:
            Response: The response of the request.
        """
        return self._request("delete", url, **kwargs)


def create_test_app(app: App, base_url: str = "http://testserver") -> App:
    """Create a test app.

    It add a test session to the app existing app object to make it usable for testing.
    The test session is be added as a property called `test_session`.
    """

    def test_session(_) -> TestSession:
        """Return the test session.

        Returns:
            TestSession: The test session.
        """
        return TestSession(base_url, RequestsWSGIAdapter(app))

    setattr(type(app), "test_session", property(test_session))

    return app
