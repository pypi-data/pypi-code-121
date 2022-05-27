"""
Resource 
"""
import requests
from typing import Dict
from scythe.exceptions import (
    NotFoundError, NotAuthorizedError, InvalidDataError, TooManyRequestsError,
    ScytheError, MultipleResultsError
)


class Response(object):
    def __init__(self, data: Dict, success: bool, status_code: int, error_message: str = None):
        self.data = data
        self.success = success
        self.status_code = status_code
        self.error_message = error_message


class RequestClient(object):

    def __init__(self, api_key, api_base, api_version):
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version
        self._create_session()

    def _create_session(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100, pool_maxsize=100
        )
        # Test Mode
        if self.api_base.startswith('http://'):
            self.session.mount('http://', adapter)
        else:
            self.session.mount('https://', adapter)

    def build_request(
        self,
        method,
        url,
        params=None
    ):
        """
        Constructing request
        """

        if self.api_key is None:
            raise ValueError("No API key provided")

        rheaders = self.build_headers(
            api_key=self.api_key,
            method=method
        )

        # Build URL
        rurl = f"{self.api_base.rstrip('/')}/{self.api_version}/{url}/"

        return rurl, rheaders

    def build_headers(self, api_key: str, method: str) -> Dict:
        """Constructing request headers"""
        if method in ("post", "put", "delete"):
            return {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }
        return {'Authorization': f'Token {api_key}'}

    def raise_exception(self, url: str, response: requests.Response, params: Dict = None):
        if response.status_code == 400:
            param_display = ""
            if params != None:
                param_display = ''.join(
                    [f'{key}={value}' for key, value in params.items()])
            raise NotFoundError(f"{url} not found with params {param_display}")

        elif response.status_code == 404:
            raise InvalidDataError("invalid data")

        elif response.status_code == 403:
            raise NotAuthorizedError("not authorized")

        elif response.status_code == 429:
            raise TooManyRequestsError("too many requests")

        elif response.status_code >= 500:
            raise ScytheError("scythe error")

    def proecss_response(self,
                         url: str,
                         response: requests.Response,
                         params: Dict = None,
                         single_object: bool = False,
                         raise_exception: bool = True):
        if response.status_code == 200:
            # Process single_object response (fetch)
            if single_object:

                # To Many Results
                if len(response.json().get('results', [])) > 1:
                    if raise_exception:
                        raise MultipleResultsError(
                            f"returned {len(response.json().get('results', []))} results")
                    return Response(
                        data={}, success=False, status_code=400
                    )

                # No results returned
                elif len(response.json().get('results', [])) == 0:
                    if raise_exception:
                        param_display = ""
                        if params != None:
                            param_display = ''.join(
                                [f'{key}={value}' for key, value in params.items()])
                        raise NotFoundError(
                            f"{url} not found with params {param_display}")
                    return Response(
                        data={}, success=False, status_code=400
                    )

                # Successful response
                else:
                    return Response(
                        data=response.json().get('results')[0], success=True,
                        status_code=response.status_code
                    )

            return Response(
                data=response.json(), success=True, status_code=response.status_code
            )

        ## Raise Response
        if raise_exception:
            self.raise_exception(url=url, params=params, response=response)

        return Response(
            data={}, success=False, error_message=response.text,
            status_code=response.status_code
        )

    def get(self, url: str, params: Dict = None, single_object: bool = False, raise_exception: bool = False):
        rurl, rheaders = self.build_request(method="get", url=url)
        response = self.session.get(
            url=rurl, headers=rheaders, params=params
        )

        return self.proecss_response(
            url=url, params=params, response=response, single_object=single_object,
            raise_exception=raise_exception
        )

    def post(self, url: str, data: Dict, raise_exception: bool = False):
        rurl, rheaders = self.build_request(method="post", url=url)
        response = self.session.post(
            url=rurl, headers=rheaders, data=data
        )

        return self.proecss_response(
            url=url, response=response, raise_exception=raise_exception
        )

    def put(self, url: str, data: Dict, raise_exception: bool = False):
        rurl, rheaders = self.build_request(method="put", url=url)
        response = self.session.put(
            url=rurl, headers=rheaders, data=data
        )

        return self.proecss_response(
            url=url, response=response, raise_exception=raise_exception
        )

    def delete(self, url: str, data: Dict, raise_exception: bool = False):
        rurl, rheaders = self.build_request(method="delete", url=url)
        response = self.session.delete(
            url=rurl, headers=rheaders, data=data
        )

        return self.proecss_response(
            url=url, response=response, raise_exception=raise_exception
        )
