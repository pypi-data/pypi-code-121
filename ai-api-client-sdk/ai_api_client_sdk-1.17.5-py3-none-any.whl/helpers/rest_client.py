import json
from typing import Callable, Dict, Union

import humps
import requests

from ai_api_client_sdk.exception import AIAPIAuthorizationException, AIAPIInvalidRequestException, \
    AIAPINotFoundException, AIAPIPreconditionFailedException, AIAPIRequestException, AIAPIServerException


class RestClient:
    """RestClient is the class implemented for sending the requests to the server.

    :param base_url: Base URL of the server. Should include the base path as well. (i.e., "<base_url>/scenarios" should
        work)
    :type base_url: str
    :param get_token: the function which returns the Bearer token, when called
    :type get_token: Callable[[], str]
    :param resource_group: The default resource group which will be used while sending the requests to the server,
        defaults to None
    :type resource_group: str
    """

    def __init__(self, base_url: str, get_token: Callable[[], str], resource_group: str = None):
        self.base_url: str = base_url
        self.get_token: Callable[[], str] = get_token
        self.resource_group_header: str = 'AI-Resource-Group'
        self.headers: dict = {}
        if resource_group:
            self.headers[self.resource_group_header] = resource_group

    def _handle_request(self, method: str, path: str, params: Dict[str, str] = None,
                        body_json: Dict[str, Union[str, dict]] = None, resource_group: str = None) -> dict:
        error_description = f'Failed to {method.lower()} {path}'

        requests_function = getattr(requests, method)
        url = f'{self.base_url}{path}'
        headers = self.headers.copy()
        headers['Authorization'] = self.get_token()
        if resource_group:
            headers[self.resource_group_header] = resource_group
        if body_json:
            body_json = humps.camelize(body_json)
        if params:
            params = humps.camelize(params)
        try:
            response = requests_function(url=url, params=params, json=body_json, headers=headers)
            if response.status_code == 401:
                raise AIAPIAuthorizationException(description=error_description, error_message=response.text)
            try:
                response_json = response.json()
            except json.decoder.JSONDecodeError:
                response_json = response.text
        except AIAPIAuthorizationException as ae:
            raise ae
        except Exception as e:
            raise AIAPIRequestException(error_description, 500) from e
        if type(response_json) is dict and 'error' in response_json:
            status_code = response.status_code
            error_message = response_json['error']['message']
            error_code = response_json['error']['code']
            request_id = response_json['error'].get('requestId')
            error_details = response_json['error'].get('details')
            if status_code == 400:
                raise AIAPIInvalidRequestException(description=error_description, error_message=error_message,
                                                   error_code=error_code, request_id=request_id, details=error_details)
            elif status_code == 404:
                raise AIAPINotFoundException(description=error_description, error_message=error_message,
                                             error_code=error_code, request_id=request_id, details=error_details)
            elif status_code == 412:
                raise AIAPIPreconditionFailedException(description=error_description, error_message=error_message,
                                                       error_code=error_code, request_id=request_id,
                                                       details=error_details)
            else:
                raise AIAPIServerException(status_code=status_code, description=error_description,
                                           error_message=error_message, error_code=error_code, request_id=request_id,
                                           details=error_details)
        elif response.status_code // 100 != 2:
            raise AIAPIServerException(description=error_description, error_message=response.text,
                                       status_code=response.status_code)
        return humps.decamelize(response_json)

    def post(self, path: str, body: Dict[str, Union[str, dict]] = None, resource_group: str = None) -> dict:
        """Sends a POST request to the server.

        :param path: path of the endpoint the request should be sent to
        :type path: str
        :param body: body of the request, defaults to None
        :type body: Dict[str, str], optional
        :param resource_group: Resource Group which the request should be sent on behalf. Either this, or the
            resource_group property of this class should be set.
        :type resource_group: str
        :raises: class:`ai_api_client_sdk.exception.AIAPIInvalidRequestException` if a 400 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthorizationException` if a 401 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPINotFoundException` if a 404 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIPreconditionFailedException` if a 412 response is received from
            the server
        :raises: class:`ai_api_client_sdk.exception.AIAPIServerException` if a non-2XX response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIRequestException` if an unexpected exception occurs while
            trying to send a request to the server
        :return: The JSON response from the server (The keys decamelized)
        :rtype: dict
        """
        return self._handle_request('post', path=path, body_json=body, resource_group=resource_group)

    def get(self, path: str, params: Dict[str, str] = None, resource_group: str = None) -> Union[dict, int]:
        """Sends a GET request to the server.

        :param path: path of the endpoint the request should be sent to
        :type path: str
        :param params: parameters of the request, defaults to None
        :type params: Dict[str, str], optional
        :param resource_group: Resource Group which the request should be sent on behalf. Either this, or the
            resource_group property of this class should be set.
        :type resource_group: str
        :raises: class:`ai_api_client_sdk.exception.AIAPIInvalidRequestException` if a 400 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthorizationException` if a 401 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPINotFoundException` if a 404 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIPreconditionFailedException` if a 412 response is received from
            the server
        :raises: class:`ai_api_client_sdk.exception.AIAPIServerException` if a non-2XX response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIRequestException` if an unexpected exception occurs while
            trying to send a request to the server
        :return: The JSON response from the server (The keys decamelized)
        :rtype: Union[dict, int]
        """
        return self._handle_request('get', path=path, params=params, resource_group=resource_group)

    def patch(self, path: str, body: Dict[str, Union[str, dict]], resource_group: str = None) -> dict:
        """Sends a PATCH request to the server.

        :param path: path of the endpoint the request should be sent to
        :type path: str
        :param body: body of the request, defaults to None
        :type body: Dict[str, str], optional
        :param resource_group: Resource Group which the request should be sent on behalf. Either this, or the
            resource_group property of this class should be set.
        :type resource_group: str
        :raises: class:`ai_api_client_sdk.exception.AIAPIInvalidRequestException` if a 400 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthorizationException` if a 401 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPINotFoundException` if a 404 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIPreconditionFailedException` if a 412 response is received from
            the server
        :raises: class:`ai_api_client_sdk.exception.AIAPIServerException` if a non-2XX response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIRequestException` if an unexpected exception occurs while
            trying to send a request to the server
        :return: The JSON response from the server (The keys decamelized)
        :rtype: dict
        """
        return self._handle_request('patch', path=path, body_json=body, resource_group=resource_group)

    def delete(self, path: str, params: Dict[str, str] = None, resource_group: str = None) -> dict:
        """Sends a DELETE request to the server.

        :param path: path of the endpoint the request should be sent to
        :type path: str
        :param params: parameters of the request, defaults to None
        :type params: Dict[str, str], optional
        :param resource_group: Resource Group which the request should be sent on behalf. Either this, or the
            resource_group property of this class should be set.
        :type resource_group: str
        :raises: class:`ai_api_client_sdk.exception.AIAPIInvalidRequestException` if a 400 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthorizationException` if a 401 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPINotFoundException` if a 404 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIPreconditionFailedException` if a 412 response is received from
            the server
        :raises: class:`ai_api_client_sdk.exception.AIAPIServerException` if a non-2XX response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIRequestException` if an unexpected exception occurs while
            trying to send a request to the server
        :return: The JSON response from the server (The keys decamelized)
        :rtype: dict
        """
        return self._handle_request('delete', path=path, params=params, resource_group=resource_group)
