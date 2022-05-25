import logging
from urllib.parse import urljoin
import requests

VERSION = '0.1.0'

logger = logging.getLogger('feedbackcompany')


class FeedbackCompanyAPI(object):
    """
    Client for the Feedback Company API.

    :param client_id: The client id
    :param client_secret: The client secret
    :param access_token: Optional access token. Omit to request a new one.

    Since access tokens are valid for multiple days, you can improve performance by storing
    self.access_token somewhere and passing it to the constructor in future calls.
    The access token is automatically renewed if it is no longer valid.
    """
    version = 'v2'
    base_url = 'https://feedbackcompany.com/api/'

    def __init__(self, client_id: str, client_secret: str, access_token: str = ''):
        self.client_id = client_id
        self.client_secret = client_secret
        if access_token:
            self.access_token = access_token
        else:
            self.renew_token()
        self.session = self.get_session()

    def get_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Authorization': 'Bearer %s' % self.access_token,
            'User-Agent': 'FeedbackCompanyAPI for Python %s' % VERSION,
            'Accept': 'application/json',
        })
        return session

    def get(self, resource_path: str):
        """
        Performs a GET request to the endpoint identified by the resource path.

        :param resource_path: The resource path.
        :return: Decoded JSON response.
        """
        response = self.session.get(
            url=self._get_url(resource_path),
        )
        try:
            return self._process_response(response)
        except FeedbackCompanyAPI.Unauthorized:
            self.renew_token()
            response = self.session.get(
                url=self._get_url(resource_path),
            )
            return self._process_response(response)

    def post(self, resource_path: str, data: dict):
        """
        Performs a POST request to the endpoint identified by the resource path.

        :param resource_path: The resource path.
        :param data: The data to send to the server.
        :return: The decoded JSON response.
        """
        response = self.session.post(
            url=self._get_url(resource_path),
            json=data,
        )
        try:
            return self._process_response(response)
        except FeedbackCompanyAPI.Unauthorized:
            self.renew_token()
            response = self.session.post(
                url=self._get_url(resource_path),
                json=data,
            )
            return self._process_response(response)

    def patch(self, resource_path: str, data: dict):
        """
        Performs a PATCH request to the endpoint identified by the resource path.

        :param resource_path: The resource path.
        :param data: The data to send to the server.
        :return: The decoded JSON response.
        """
        response = self.session.patch(
            url=self._get_url(resource_path),
            json=data,
        )
        try:
            return self._process_response(response)
        except FeedbackCompanyAPI.Unauthorized:
            self.renew_token()
            response = self.session.patch(
                url=self._get_url(resource_path),
                json=data,
            )
            return self._process_response(response)

    def delete(self, resource_path: str):
        """
        Performs a DELETE request to the endpoint identified by the resource path.

        :param resource_path: The resource path.
        :return: The decoded JSON response.
        """
        response = self.session.delete(
            url=self._get_url(resource_path),
        )
        try:
            return self._process_response(response)
        except FeedbackCompanyAPI.Unauthorized:
            self.renew_token()
            response = self.session.delete(
                url=self._get_url(resource_path),
            )
            return self._process_response(response)

    def renew_token(self):
        """
        Update self.access_token with a newly created token.
        """
        logger.debug("Requesting new access token...")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FeedbackCompanyAPI for Python %s' % VERSION,
            'Accept': 'application/json',
        })
        url = 'https://www.feedbackcompany.com/api/v2/oauth2/token'
        url += '?grant_type=authorization_code&client_id=%s&client_secret=%s' % (self.client_id, self.client_secret)
        response = self._process_response(self.session.get(url))
        if response['error'] or 'access_token' not in response:
            raise FeedbackCompanyAPI.UnexpectedResponseError('Could not obtain access token.')
        self.access_token = response['access_token']
        self.session = self.get_session()
        return self.access_token

    @classmethod
    def _get_url(cls, resource_path: str):
        """
        Builds the URL to the API endpoint specified by the given parameters.

        :param resource_path: The path to the resource.
        :return: The absolute URL to the endpoint.
        """
        return urljoin(cls.base_url, '%s/%s.json' % (cls.version, resource_path))

    @staticmethod
    def _process_response(response: requests.Response, expected: list = []) -> dict:
        """
        Processes an API response. Raises an exception when appropriate.

        The exception that will be raised is FeedbackCompanyAPI.Error.
        This exception is subclassed so implementing programs can easily react appropriately to different exceptions.

        The following subclasses of FeedbackCompanyAPI.Error can be raised:
          - FeedbackCompanyAPI.Unauthorized: No access to the resource or invalid authentication
          - FeedbackCompanyAPI.NotFound: Resource not found, check resource path
          - FeedbackCompanyAPI.InvalidData: Validation errors occurred while processing your input
          - FeedbackCompanyAPI.ServerError: Error on the server

        :param response: The response to process.
        :param expected: A list of expected status codes which won't raise an exception.
        :return: The useful data in the response (may be None).
        """
        responses = {
            200: None,
            201: None,
            204: None,
            400: FeedbackCompanyAPI.Unauthorized,
            401: FeedbackCompanyAPI.Unauthorized,
            404: FeedbackCompanyAPI.NotFound,
            406: FeedbackCompanyAPI.NotFound,
            422: FeedbackCompanyAPI.InvalidData,
            500: FeedbackCompanyAPI.ServerError,
        }

        logger.debug("API request: %s %s\n" % (response.request.method, response.request.url) +
                     "Response: %s %s" % (response.status_code, response.text))

        if response.status_code not in expected:
            if response.status_code not in responses:
                logger.error("API response contained unknown status code")
                raise FeedbackCompanyAPI.APIError(response, "API response contained unknown status code")
            elif responses[response.status_code] is not None:
                try:
                    description = response.json()['error']
                except (AttributeError, TypeError, KeyError, ValueError):
                    description = None
                raise responses[response.status_code](response, description)

        try:
            data = response.json()
        except ValueError:
            logger.error("API response is not JSON decodable")
            data = None

        return data

    class UnexpectedResponseError(Exception):
        pass

    class APIError(Exception):
        """
        Exception for cases where communication with the API went wrong.

        This exception is specialized into a number of exceptions with the exact same properties.
        """
        def __init__(self, response: requests.Response, description: str = None):
            """
            :param response: The API response.
            :param description: Description of the error.
            """
            self._response = response
            msg = 'API error %d' % response.status_code
            if description:
                msg += ': %s' % description
            super(FeedbackCompanyAPI.APIError, self).__init__(msg)

        @property
        def status_code(self):
            """
            HTTP status code of the request.
            """
            return self._response.status_code

        @property
        def response(self):
            """
            JSON encoded data of the response.
            """
            return self._response.json()

        @property
        def request(self):
            """
            Short string representation of the request (method and URL).
            """
            return '%s %s' % (self._response.request.method, self._response.request.url)

    class Unauthorized(APIError):
        pass

    class NotFound(APIError):
        pass

    class InvalidData(APIError):
        pass

    class ServerError(APIError):
        pass