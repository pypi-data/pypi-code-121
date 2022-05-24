"""
request handler with its dependencies to intercept http requests
"""
import enum
import os
import os.path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests
from requests import Response

from .._version import __version__ as SAAS_CLIENT_VERSION
from ..auth.model.credentials import CredentialsBase
from ..auth.oauth import OAuthService
from ..config.configuration import Configuration

COOKIE_HEADER = 'Cookie'


class DataSupportedMediaType(enum.Enum):
    """
    Supported Content types for Dict[str, str] and List[Tuple[str, str]]
    """

    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    MULTIPART_FORM_DATA = 'multipart/form-data'


class PayloadSupportedMediaType(enum.Enum):
    """
    Supported Content types for Dict[str, object]
    """

    APPLICATION_JSON = 'application/json'


class ContentType(enum.Enum):
    """
    Supported Content types
    """

    FORM_URL_ENCODED = DataSupportedMediaType.FORM_URL_ENCODED.value
    MULTIPART_FORM_DATA = DataSupportedMediaType.MULTIPART_FORM_DATA.value
    APPLICATION_JSON = PayloadSupportedMediaType.APPLICATION_JSON.value


def to_content_type_enum(content_type: str) -> ContentType:
    """
    to_content_type_enum is used for mapping a string to ContentType enum.
    :param content_type: To be used to map to ContentType
    :type content_type: str
    """
    content_type_map = {
        ContentType.MULTIPART_FORM_DATA.value: ContentType.MULTIPART_FORM_DATA,
        ContentType.FORM_URL_ENCODED.value: ContentType.FORM_URL_ENCODED,
        ContentType.APPLICATION_JSON.value: ContentType.APPLICATION_JSON
    }

    content_type_enum = content_type_map.get(content_type)

    if content_type_enum:
        return content_type_enum

    raise ValueError(f'{content_type} is not supported!')


class _RequestHandler:
    def __init__(self, credentials: CredentialsBase, configuration: Configuration) -> None:
        super().__init__()

        self.__credentials = credentials
        self.__oauth_service = OAuthService(configuration)
        self.__cookie = self.__oauth_service.login(self.__credentials)
        self.__configuration = configuration
        self.__csrf_token = self._get_csrf_token()
        self.__default_headers = self._get_default_headers()

    def _get_csrf_token(self) -> str:
        # Make a request to get the csrf token
        hs_server_url = f'https://{self.__configuration.hs_domain}'
        message = self._create_request_message(hs_server_url, [], 'GET', None)
        self.__default_headers = self._get_default_headers(include_csrf=False)
        res = self._send_request(message)
        res.raise_for_status()
        return res.cookies.get('csrftoken')

    def handle_request(
        self,
        url: str,
        data: Union[Dict[str, Any], List[Tuple[str, Any]]] = None,
        method: str = 'GET',
        content_type: Union[DataSupportedMediaType, PayloadSupportedMediaType] = None,
    ) -> Response:
        """
        handle request is building and sending requests to the server
        :param url: relative endpoint to invoke
        :type url: str
        :param data: data to be sent to the server
        :type data: Union[Dict[str, str], List[Tuple[str, str]]]
        :param method: HTTP method to invoke
        :type method: str
        :param content_type: ContentType of the request
        :type content_type: Union[DataSupportedMediaType, PayloadSupportedMediaType]
        :return: Server's response
        :rtype: Response
        """
        internal_content_type = None
        if content_type:
            internal_content_type = to_content_type_enum(content_type.value)
        data = self.to_tuple_list(data)
        prepared_url = urljoin(f'https://{self.__configuration.hs_domain}', url)
        message = self._create_request_message(prepared_url, data, method, internal_content_type)
        res = self._send_request(message)
        if self._is_session_expired(res):
            self.__cookie = self.__oauth_service.login(self.__credentials)
            self.__csrf_token = self._get_csrf_token()
            self.__default_headers = self._get_default_headers()
            message = self._create_request_message(prepared_url, data, method, internal_content_type)
            res = self._send_request(message)

        return res

    @staticmethod
    def to_tuple_list(
            data: Union[Dict[str, Any], List[Tuple[str, Any]], None]
    ) -> List[Tuple[str, object]]:
        """
        Synthesize supported data into List of tuples
        :param data: list, dictionary or None default value
        :type data: Union[Dict[str, Any], List[Tuple[str, Any]], None]
        :return: data converted into list
        :rtype: List[Tuple[str, object]]
        """
        data = data or []
        if isinstance(data, dict):
            data = list(data.items())
        return data

    def _send_request(self, message: Dict[str, Any]) -> Response:
        message['headers'].update(self.__default_headers)
        message['allow_redirects'] = False
        message['timeout'] = self.__configuration.request_timeout
        response = requests.request(**message)
        response.close()
        return response

    def _is_session_expired(self, res: Response) -> bool:
        redirect_header = res.headers.get('Location', '')
        is_cookie_expired = (
            res.status_code == 302 and self.__configuration.auth_server in redirect_header
        )
        is_csrf_token_expired = res.status_code == 403 and 'CSRF Failed' in res.text
        return is_cookie_expired or is_csrf_token_expired

    def _get_default_headers(self, include_csrf: bool = True) -> Dict[str, str]:
        headers = {
            'User-Agent': f'hyperscience-saas-client-python/{SAAS_CLIENT_VERSION}',
            COOKIE_HEADER: self.__cookie,
        }
        if include_csrf and self.__csrf_token:
            headers['X-CSRFToken'] = self.__csrf_token
            headers['Referer'] = f'https://{self.__configuration.hs_domain}'
            headers[COOKIE_HEADER] = f'csrftoken={self.__csrf_token}; {self.__cookie}'
        return headers

    def _create_request_message(
        self,
        url: str,
        data: List[Tuple[str, object]],
        method: str,
        content_type: Optional[ContentType],
    ) -> Dict[str, str]:
        switcher = {
            'POST': lambda: self._create_post_message(url, data, method, content_type),
            'GET': lambda: self._create_get_message(url, data, method, content_type),
        }
        create_message = switcher.get(method, lambda: {})
        request_message = create_message()
        if len(request_message) == 0:
            raise ValueError(f'{method} is not a supported operation')
        return request_message

    @staticmethod
    def _create_post_message(
        url: str, data: List[Tuple[str, object]], method: str, content_type: Optional[ContentType]
    ) -> dict:
        if content_type is ContentType.FORM_URL_ENCODED:
            post_message = {
                'url': url,
                'method': method,
                'data': data,
                'headers': {'Content-Type': content_type.value},
            }
        elif content_type is ContentType.MULTIPART_FORM_DATA:
            # we close files opened in hooks handled by requests hooks below
            files = [
                (k, open(str(v), 'rb'))  # pylint: disable=R
                for (k, v) in data if os.path.isfile(str(v))
            ]
            filtered_data = [(k, v) for (k, v) in data if not os.path.isfile(str(v))]
            post_message = {
                'url': url,
                'method': method,
                'files': files,
                'data': filtered_data,
                'headers': {},
                'hooks': {
                    'response': lambda res, *args, **kwargs: _RequestHandler._close_files(files)
                },
            }
        elif content_type is ContentType.APPLICATION_JSON:
            post_message = {
                'url': url,
                'method': method,
                'json': dict(data),
                'headers': {'Content-Type': content_type.value},
            }
        else:
            raise ValueError(f'{content_type} is not supported!')

        return post_message

    @staticmethod
    def _close_files(files: List[Tuple[str, BinaryIO]]) -> None:
        for _, file in files:
            file.close()

    @staticmethod
    def _create_get_message(
        url: str, data: List[Tuple[str, object]], method: str, content_type: Optional[ContentType]
    ) -> dict:
        headers = {'Content-Type': content_type.value} if content_type else {}
        return {'url': url, 'method': method, 'params': data, 'headers': headers}
