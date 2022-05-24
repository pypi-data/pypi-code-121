"""
api controller module
"""
from typing import Dict, List, Tuple, Union

from requests import Response

from ..auth.model.credentials import CredentialsBase, EnvironmentCredentialsProvider
from ..config.configuration import Configuration
from .model.http_verb import HttpVerb
from .request_handler import _RequestHandler, DataSupportedMediaType, PayloadSupportedMediaType


class ApiController:
    """
    ApiController class enables client sending api requests to hyperscience platform
    """

    def __init__(
            self,
            configuration: Configuration,
            credentials: CredentialsBase = EnvironmentCredentialsProvider(),
    ):
        """
        ApiController is used for interacting with hyperscience platform.
        :param credentials: CredentialsProvider to be used
        :type credentials: CredentialsBase
        :param configuration: Configuration to be used
        :type configuration: Configuration
        """
        self.__request_handler = _RequestHandler(credentials, configuration)

    def get(
            self,
            url: str,
            data: Union[Dict[str, str], List[Tuple[str, str]]] = None,
            content_type: DataSupportedMediaType = None,
    ) -> Response:
        """
        Send get request.
        :param url: relative endpoint to invoke
        :type url: str
        :param data: query params in the form of key, value pairs
        :type data: Union[Dict[str,str], List[Tuple[str,str]]]
        :param content_type: content type of the request
        :type content_type: ContentType
        :return: HTTP GET call response
        :rtype: requests.Response
        """

        res = self.__request_handler.handle_request(
            url,
            data,
            HttpVerb.GET.value,
            content_type)
        return res

    def post(
            self,
            url: str,
            data: Union[Dict[str, object], List[Tuple[str, str]]],
            content_type: Union[PayloadSupportedMediaType, DataSupportedMediaType]
    ) -> Response:
        """
        Send post request.
        :param url: relative endpoint to invoke
        :type url: str
        :param data: parameters for post in the form of key, value pairs
        :type data: Union[Dict[str,object], List[Tuple[str,str]]]
        :param content_type: content type of the request
        :type content_type: Union[PayloadSupportedMediaType, DataSupportedMediaType]
        :return: HTTP POST call response
        :rtype: requests.Response
        """
        return self.__request_handler.handle_request(
            url,
            data,
            HttpVerb.POST.value,
            content_type)
