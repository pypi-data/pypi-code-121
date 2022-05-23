"""Templates for generated code"""

ACCESS_FILE_HEAD_TEMPLATE = """
        \"""Definition of {Section} access methods.\"""
        import urllib.parse
        from typing import TYPE_CHECKING, Dict{ImportTypes}

        from trustedtwin.misc import RESTMethod
        from trustedtwin.models.responses import process_response

        if TYPE_CHECKING:
            from trustedtwin.service import RestService
            
        # WARNING: This code has been generated automatically, do not modify unless you know what you are doing.
        """


ACCESS_CLASS_HEAD_TEMPLATE = """
        class {Section}Operations:
            \"""Interfaces for accessing {Section} API operations\"""

            def __init__(self, service: 'RestService'):
                \"""Initialize object\"""
                self._service = service
                self._http_client = self._service.http_client
        """

ACCESS_METHOD_TEMPLATE = """
            def {MethodMame}({Arguments}) -> Dict:
                \"""Execute {OperationName} API operation\"""

                endpoint = {Endpoint}
                endpoint = urllib.parse.quote(endpoint)
                {ParamsLine}
                {ParamsFilterLine}
                resp = self._http_client.execute_request(
                    method=RESTMethod.{RESTMethod},
                    url_root=self._http_client.host_name,
                    endpoint=endpoint{PassParams}{PassBody}
                )

                return process_response(resp, '{OperationName}', **self._service.kwargs)
            """

CLIENT_FILE_HEADER_TEMPLATE = """\
\"""RestService access operations\"""
import logging
from typing import Any

from trustedtwin.http_client import HTTPClient
{OperationsImports}

logger = logging.getLogger("trusted_twin")


DEFAULT_TT_API_HOST = "https://rest.trustedtwin.com"

# WARNING: This code has been generated automatically, do not modify unless you know what you are doing.
"""

CLIENT_CLASS_HEAD_TEMPLATE = """
class RestService:
    \"""Represents client accessing API\"""

    def __init__(self, auth: str, api_host: str = DEFAULT_TT_API_HOST, **kwargs: Any):
        \"""Initialize object

        :param api_host: url to api host
        :param auth: Authorization secret
        \"""
        self.http_client = HTTPClient(auth, api_host)
        self.kwargs = kwargs
"""

CLIENT_METHOD_TEMPLATE = """
    @property
    def {Section}(self) -> {SectionCap}Operations:
        \"""Return {SectionCap} related API operations\"""
        return {SectionCap}Operations(self)
"""
