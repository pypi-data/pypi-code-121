import uuid
from urllib.parse import urljoin

from .http_utils import get_session
from .mixins import (
    AuthMixin,
    BankStatementMixin,
    CibilMixin,
    ExperianMixin,
    HighmarkMixin,
    IDVerificationMixin,
    MailMixin,
    SMSMixin,
    WebhookMixin,
)


class MercuryApi(
    AuthMixin,
    BankStatementMixin,
    CibilMixin,
    ExperianMixin,
    HighmarkMixin,
    IDVerificationMixin,
    MailMixin,
    SMSMixin,
    WebhookMixin,
):
    """
    Mercury client to connect to the mercury service

    """

    def __init__(self, conn_params=None):
        self.username = conn_params["username"]
        self.password = conn_params["password"]
        self.host = conn_params["url"]
        self._access_token = None
        self._refresh_token = None
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = get_session()

        return self._session

    @staticmethod
    def _generate_mercury_request_id():
        """
        Generate Unique request id
        :return:
        """
        return uuid.uuid4().hex

    def _get_request_url_from_path(self, path):
        url = urljoin(self.host, path)
        return url

    def _post_json_http_request(
        self, path, data, headers=None, send_request_id=True, add_bearer_token=True
    ):
        """
        Perform POST request on the provided API with the provided data

        :param path: The path to send the HTTP POST. This will be combined with the
            configured host
        :param data: dict to be sent as JSON in the HTTP body
        :param headers: headers for the request
        :param send_request_id: Defaults to True. Indicates if a request Id has to
        generated for the request
        :param add_bearer_token: Defaults to True. If True, we will add the bearer token
        to the request
        :return: (request_id, response): The request id (if present) and the response
        """
        if headers is None:
            headers = dict()

        if send_request_id:
            headers["X-Mercury-Request-Id"] = self._generate_mercury_request_id()

        if add_bearer_token:
            headers["Authorization"] = "Bearer {}".format(self.access_token)

        url = self._get_request_url_from_path(path)
        r = self.session.post(url=url, json=data, headers=headers, timeout=10)

        return headers.get("X-Mercury-Request-Id"), r

    def _get_json_http_request(
        self, path, headers=None, send_request_id=True, add_bearer_token=True
    ):
        """
        Perform GET request on the provided URL

        :param url: The path to send the HTTP POST. This will be combined with the
            configured host
        :type url: str
        :param headers: Headers for the request, defaults to None
        :type headers: dict, optional
        :param send_request_id: Indicates if a request ID has to be generated for the
        request, defaults to True
        :type send_request_id: bool, optional
        :param add_bearer_token: If True, will add a bearer token to the request,
        defaults to True
        :type add_bearer_token: bool, optional
        :return: (request_id, response) The request ID and the response
        :rtype: (str, str)
        """
        if headers is None:
            headers = dict()

        if send_request_id:
            headers["X-Mercury-Request-Id"] = self._generate_mercury_request_id()

        if add_bearer_token:
            headers["Authorization"] = "Bearer {}".format(self.access_token)

        url = self._get_request_url_from_path(path)
        r = self.session.get(url=url, headers=headers, timeout=10)

        return headers.get("X-Mercury-Request-Id"), r
