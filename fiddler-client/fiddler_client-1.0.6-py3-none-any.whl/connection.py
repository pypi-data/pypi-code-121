import configparser
import contextlib
import json
import logging
import os
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from packaging import version
from requests.exceptions import Timeout
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ._version import __version__
from .utils.exceptions import JSONException, ResourceNotFound

LOG = logging.getLogger(__name__)

SIMPLE_RES_API = ['slice_query', 'parse_slice_query']


class Connection:

    SUCCESS_STATUS = 'SUCCESS'
    FAILURE_STATUS = 'FAILURE'
    AUTH_HEADER_KEY = 'Authorization'
    STREAMING_HEADER_KEY = 'X-Fiddler-Results-Format'
    FIDDLER_ARGS_KEY = '__fiddler_args__'
    ROUTING_HEADER_KEY = 'x-fdlr-fwd'

    """Broker of all connections to the Fiddler API.
    Conventions:
        - Exceptions are raised for FAILURE reponses from the backend.
        - Methods beginning with `list` fetch lists of ids (e.g. all model ids
            for a project) and do not alter any data or state on the backend.
        - Methods beginning with `get` return a more complex object but also
            do not alter data or state on the backend.
        - Methods beginning with `run` invoke model-related execution and
            return the result of that computation. These do not alter state,
            but they can put a heavy load on the computational resources of
            the Fiddler engine, so they should be paralellized with care.
        - Methods beginning with `delete` permanently, irrevocably, and
            globally destroy objects in the backend. Think "rm -rf"
        - Methods beginning with `upload` convert and transmit supported local
            objects to Fiddler-friendly formats loaded into the Fiddler engine.
            Attempting to upload an object with an identifier that is already
            in use will result in an exception being raised, rather than the
            existing object being overwritten. To update an object in the
            Fiddler engine, please call both the `delete` and `upload` methods
            pertaining to the object in question.

    :param url: The base URL of the API to connect to. Usually either
        https://dev.fiddler.ai (cloud) or http://localhost:4100 (onebox)
    :param org_id: The name of your organization in the Fiddler platform
    :param auth_token: Token used to authenticate. Your token can be
        created, found, and changed at <FIDDLER URL>/settings/credentials.
    :param proxies: optionally, a dict of proxy URLs. e.g.,
                    proxies = {'http' : 'http://proxy.example.com:1234',
                               'https': 'https://proxy.example.com:5678'}
    :param verbose: if True, api calls will be logged verbosely,
                    *warning: all information required for debugging will be
                    logged including the auth_token.
    """

    def __init__(
        self,
        url=None,
        org_id=None,
        auth_token=None,
        proxies=None,
        verbose=False,
        verify=True,
    ):
        self._verify = verify
        if Path('fiddler.ini').is_file():
            config = configparser.ConfigParser()
            config.read('fiddler.ini')
            info = config['FIDDLER']
            if not url:
                url = info['url']
            if not org_id:
                org_id = info['org_id']
            if not auth_token:
                auth_token = info['auth_token']

        if url[-1] == '/':
            raise ValueError('url should not end in "/"')

        # use session to preserve session data
        self.session = requests.Session()
        self.session.verify = self._verify
        if proxies:
            assert isinstance(proxies, dict)
            self.session.proxies = proxies
        self.adapter = requests.adapters.HTTPAdapter(
            pool_connections=25,
            pool_maxsize=25,
        )
        self.session.mount(url, self.adapter)
        self.url = url
        self.org_id = org_id
        self.auth_header = {self.AUTH_HEADER_KEY: f'Bearer {auth_token}'}
        self.streaming_header = {self.STREAMING_HEADER_KEY: 'application/jsonlines'}
        self.verbose = verbose
        self.strict_mode = True
        self.capture_server_log = False
        self.last_server_log = None
        self.check_connection()

    def check_connection(self, check_client_version=True, check_server_version=True):
        try:
            path = ['get_supported_features', self.org_id]
            result = self.call(path, is_get_request=True)
            server_version = result.get('supported_client_version', __version__)
            if version.parse(server_version) > version.parse(__version__):
                LOG.info(
                    f'client_version = {__version__} < server_version = {server_version}'
                )
                if check_client_version:
                    LOG.warning(
                        f'OUTDATED CLIENT: Your client is running version {__version__}, '
                        f'consider upgrading to {server_version}.'
                    )
            elif version.parse(server_version) < version.parse(__version__):
                LOG.info(
                    f'client_version = {__version__} > server_version = {server_version}'
                )
                if check_server_version:
                    LOG.warning(
                        f'OUTDATED SERVER: The URL you connected to is running version {server_version}, '
                        f'consider getting it upgraded to match your client {__version__}.'
                    )
            else:
                LOG.info(
                    f'client_version = {__version__} == server_version = {server_version}'
                )
            return 'OK'
        except requests.exceptions.ConnectionError:
            LOG.warning(
                'CONNECTION CHECK FAILED: Unable to connect with '
                'to Fiddler. Are you sure you have the right URL?'
            )
        except Exception as e:
            LOG.exception(
                f'API CHECK FAILED: Able to connect to Fiddler, '
                f'but request failed with message:\n"{str(e)}"'
            )
            raise e

    @staticmethod
    def _get_routing_header(path_base: str) -> Dict[str, str]:
        """Returns the proper header so that a request is routed to the correct
        service."""
        # @todo: Given we check for the service in admin service using fiddler-ingress yaml, we should not be using this here. Just remove it ensuring no side effects.
        executor_service_bases = (
            'dataset_predictions',
            'execute',
            'executor',
            'explain',
            'explain_by_row_id',
            'fairness',
            'feature_importance',
            'generate',
            'new_project',
            'trigger_pre_computation',
            'precache_globals',
        )
        if path_base in executor_service_bases:
            return {Connection.ROUTING_HEADER_KEY: 'executor_service'}
        else:
            return {Connection.ROUTING_HEADER_KEY: 'data_service'}

    def _form_request(
        self,
        path: List[str],
        is_get_request: bool = None,
        json_payload: Any = None,
        stream: bool = False,
        files: Optional[List[Path]] = None,
        context_stack=None,
        endpoint=None,
    ):
        if is_get_request:
            req = requests.Request('GET', endpoint)
        else:
            # if uploading files, we use a multipart/form-data request and
            # dump the json_payload to be the special "fiddler args"
            # as a json object in the form

            if files is not None:
                # open all the files into the context manager stack
                opened_files = {
                    fpath.name: context_stack.enter_context(fpath.open('rb'))
                    for fpath in files
                }
                #
                # NOTE: there are a lot LOT of ways to do this wrong with
                # `requests`
                #
                # Take a look here (and at the thread linked) for more info:
                # https://stackoverflow.com/a/35946962
                #
                # And here: https://stackoverflow.com/a/12385661
                #
                form_data: Dict[str, Tuple[Optional[str], str, str]] = {
                    **{
                        self.FIDDLER_ARGS_KEY: (
                            None,  # filename
                            json.dumps(json_payload),  # data
                            'application/json',  # content_type
                        )
                    },
                    **{
                        fpath.name: (
                            fpath.name,  # filename
                            opened_files[fpath.name],  # data
                            'application/octet-stream',  # content_type
                        )
                        for fpath in files
                    },
                }
                # Take a look at this for how to use MultipartEncoder
                # https://stackoverflow.com/questions/12385179/how-to-send-a-multipart-form-data-with-requests-in-python/12385661#12385661

                mp_encoder = MultipartEncoder(form_data)
                req = requests.Request(
                    'POST',
                    endpoint,
                    data=mp_encoder,
                    headers={'Content-Type': mp_encoder.content_type},
                )
            else:
                req = requests.Request(
                    'POST',
                    endpoint,
                    data=json.dumps(json_payload, allow_nan=True),
                    headers={'Content-Type': 'application/json'},
                )

        # add necessary headers
        # using prepare_request from session to keep session data
        req = self.session.prepare_request(req)

        added_headers = dict()
        added_headers.update(self.auth_header)
        added_headers.update(self._get_routing_header(path[0]))
        if self.capture_server_log:
            added_headers['X-Fiddler-Logs-Level'] = 'DEBUG'
        if stream:
            added_headers.update(self.streaming_header)
        req.headers = {**added_headers, **req.headers}

        return req

    @staticmethod
    def _handle_fail_res(res, endpoint, api_name):
        """
        Raises an actionable error message for a response with a status code > 200
        """
        try:
            # catch auth failure
            json_response = res.json()
            message = json_response.get('message')
            if endpoint == '':
                error_msg = message
            elif api_name in SIMPLE_RES_API:
                error_msg = message
            else:
                error_msg = (
                    f'API call to {endpoint} failed with status {res.status_code}:'
                    f' The full response message was {message}'
                )
            # catch resource not found failure
            if res.status_code == 404:
                error = ResourceNotFound(message=message)
            elif res.status_code == 401:
                # More specific error message
                error_msg = (
                    'API call failed with status 401: '
                    'Authorization Required. '
                    'Do you have the right `org_id` and `auth_token`?'
                )
                error = RuntimeError(error_msg)
            else:
                error = JSONException(
                    status=json_response.get('status'),
                    message=error_msg,
                    stacktrace=json_response.get('stacktrace'),
                    logs=json_response.get('logs'),
                )
        except json.JSONDecodeError:
            if api_name in SIMPLE_RES_API:
                error_msg = res.txt
            else:
                error_msg = (
                    f'API call to {endpoint} failed with status {res.status_code}:'
                    f' The full response message was {res.text}'
                )
            error = RuntimeError(error_msg)
        LOG.debug(error_msg)
        raise error

    def call(
        self,
        path: List[str],
        json_payload: Any = None,
        files: Optional[List[Path]] = None,
        is_get_request: bool = False,
        stream: bool = False,
        timeout: Optional[int] = None,
        num_tries: int = 1,
    ):
        """Issues a request to the API and returns the result,
        logigng and handling errors appropriately.

        Raises a RuntimeError if the response is a failure or cannot be parsed.
        Does not handle any ConnectionError exceptions thrown by the `requests`
        library.

        Note: Parameters `timeout` and `num_tries` are currently only utilized in a workaround
        for a bug involving Mac+Docker communication. See: https://github.com/docker/for-mac/issues/3448
        """
        res: Optional[requests.Response] = None
        assert self.url is not None, 'self.url unexpectedly None'
        endpoint = '/'.join([self.url] + path)

        # set up a context manager to open files
        with contextlib.ExitStack() as context_stack:
            request_type = 'GET' if is_get_request else 'POST'

            request_excerpt: Optional[str] = None
            if json_payload:
                request_excerpt = textwrap.indent(
                    json.dumps(json_payload, indent=2)[:2048], '  '
                )

            if self.verbose:
                LOG.info(
                    f'running api call as {request_type} request\n'
                    f'to {endpoint}\n'
                    f'with headers {self.auth_header}\n'
                    f'with payload {request_excerpt}'
                )

            req = self._form_request(
                path=path,
                is_get_request=is_get_request,
                json_payload=json_payload,
                stream=stream,
                files=files,
                context_stack=context_stack,
                endpoint=endpoint,
            )

            # log the raw request
            raw_request_info = (
                f'Request:\n'
                f'  url: {req.url}\n'
                f'  method: {req.method}\n'
                f'  headers: {req.headers}'
            )
            LOG.debug(raw_request_info)

            if os.environ.get('REQUESTS_CA_BUNDLE'):
                self.session.verify = os.environ.get('REQUESTS_CA_BUNDLE')

            # send the request using session to carry auth info from login
            if 'FIDDLER_RETRY_PUBLISH' in os.environ and str(
                os.environ['FIDDLER_RETRY_PUBLISH']
            ).lower() in ['yes', 'y', 'true', '1']:
                # Experimental retry path needed in case of Mac-Docker communication bug.
                # Likely only needed in case of Onebox Mac-Docker setups, and as such only
                # accessible through this environmental variable
                attempt_count = 0
                while attempt_count < num_tries:
                    try:
                        res = self.session.send(req, stream=stream, timeout=timeout)
                        break
                    except Timeout:
                        # Retrying due to a failure of some kind
                        attempt_count += 1
                        # Exponential sleep between calls (up to 10 seconds)
                        time.sleep(min(pow(2, attempt_count), 10))
                if res is None:
                    error_msg = (
                        'API call failed due to unknown reason. '
                        'Please try again at a later point.'
                    )
                    raise Timeout(error_msg)
            else:
                res = self.session.send(req, stream=stream)

            if self.verbose:
                assert res is not None, 'res unexpectedly None'
                LOG.info(f'response: {res.text}')

        # catch any failure
        assert res is not None, 'res unexpectedly None'
        if res.status_code != 200:
            self._handle_fail_res(res, endpoint, path[0])

        if stream:
            return self._process_streaming_call_result(res, endpoint, raw_request_info)
        return self._process_non_streaming_call_result(res, endpoint, raw_request_info)

    @staticmethod
    def _raise_on_status_error(
        response: requests.Response, endpoint: str, raw_request_info: str
    ):
        """Raises exception on HTTP errors similar to
        `response.raise_for_status()`."""
        # catch non-auth failures
        try:
            response.raise_for_status()
        except Exception:
            response_payload = response.json()
            try:
                failure_message = response_payload.get('message', 'Unknown')
                failure_stacktrace = response_payload.get('stacktrace')
                error_msg = (
                    f'API call failed.\n'
                    f'Error message: {failure_message}\n'
                    f'Endpoint: {endpoint}'
                )
                if failure_stacktrace:
                    error_msg += f'\nStacktrace: {failure_stacktrace}'

            except KeyError:
                error_msg = (
                    f'API call to {endpoint} failed.\n'
                    f'Request response: {response.text}'
                )
            LOG.debug(f'{error_msg}\n{raw_request_info}')
            raise RuntimeError(error_msg)

    def _process_non_streaming_call_result(
        self, response: requests.Response, endpoint: str, raw_request_info: str
    ):

        Connection._raise_on_status_error(response, endpoint, raw_request_info)

        # catch non-JSON response (this is rare, the backend should generally
        # return JSON in all cases)
        try:
            response_payload = response.json()
        except json.JSONDecodeError:
            error_msg = (
                f'API call to {endpoint} failed.\n' f'Request response: {response.text}'
            )
            LOG.exception(f'{response.status_code}\nf{error_msg}')

            LOG.debug(f'{error_msg}\n{raw_request_info}')
            raise RuntimeError(error_msg)

        assert response_payload['status'] == self.SUCCESS_STATUS
        result = response_payload.get('result')
        self.last_server_log = response_payload.get('logs')

        # log the API call on success (excerpt response on success)
        response_excerpt = textwrap.indent(
            json.dumps(response_payload, indent=2)[:2048], '  '
        )
        log_msg = (
            f'API call to {endpoint} succeeded.\n'
            f'Request response: {response_excerpt}\n'
            f'{raw_request_info}\n'
        )
        if self.verbose:
            LOG.info(log_msg)
        return result

    @staticmethod
    def _process_streaming_call_result(
        response: requests.Response, endpoint: str, raw_request_info: str
    ):
        """Processes response in jsonlines format. `json_streaming_endpoint`
        returns jsonlines with one json object per line when
        'X-Fiddler-Response-Format' header is set to 'jsonlines'.
        :returns: a generator for results."""

        Connection._raise_on_status_error(response, endpoint, raw_request_info)

        got_eos = False  # got proper end_of_stream.

        if response.headers.get('Content-Type') != 'application/x-ndjson':
            RuntimeError('Streaming response Content-Type is not "x-ndjson"')

        # Read one line at a time. `chunk_size` None ensures that a line
        # is returned as soon as it is read, rather waiting for any minimum
        # size (default is 512 bytes).
        for line in response.iter_lines(chunk_size=None):
            if line:
                try:
                    row_json = json.loads(line)
                    if 'result' in row_json:
                        yield row_json['result']
                    elif row_json.get('status') == Connection.SUCCESS_STATUS:
                        got_eos = True
                        break
                except ValueError as valueError:
                    failure_response = {}
                    failure_response['status'] = 400
                    failure_response['message'] = 'Unable to serialize {line}'
                    failure_response['stacktrace'] = valueError
                    Connection._handle_fail_res(failure_response, '', '')

        if not got_eos:
            raise RuntimeError(
                'Truncated response for streaming request. '
                'Failed to receive successful status.'
            )

    def call_executor_service(
        self,
        path: List[str],
        json_payload: Any = None,
        files: Optional[List[Path]] = None,
        is_get_request: bool = False,
        stream: bool = False,
    ):
        no_auth_onebox = False
        try:
            if self.url == 'http://localhost:6100':
                no_auth_onebox = True
                self.url = 'http://localhost:5100'

            return self.call(path, json_payload, files, is_get_request, stream)
        finally:
            if no_auth_onebox:
                self.url = 'http://localhost:6100'
