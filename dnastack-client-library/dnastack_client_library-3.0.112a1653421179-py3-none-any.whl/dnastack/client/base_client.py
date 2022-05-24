from abc import ABC
from requests.auth import AuthBase
from typing import Optional, List
from uuid import uuid4

from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.models import ServiceEndpoint
from dnastack.common.logger import get_logger
from dnastack.http.authenticators.abstract import Authenticator
from dnastack.http.authenticators.factory import HttpAuthenticatorFactory
from dnastack.http.session import HttpSession


class BaseServiceClient(ABC):
    """ The base class for all DNAStack Clients """

    def __init__(self, endpoint: ServiceEndpoint):
        if not endpoint.url.endswith(r'/'):
            endpoint.url = endpoint.url + r'/'

        self._uuid = str(uuid4())
        self._endpoint = endpoint
        self._logger = get_logger(type(self).__name__)
        self._current_authenticator: Optional[AuthBase] = None

    @property
    def endpoint(self):
        return self._endpoint

    def __del__(self):
        self.close()

    def close(self):
        pass

    def get_http_user_agent(self) -> str:
        self_type = type(self)
        return HttpSession.generate_http_user_agent([
            f'Class/{self_type.__module__}.{self_type.__name__}',
            f'Mode/{self._endpoint.mode}',
        ])

    @staticmethod
    def get_adapter_type() -> str:
        """Get the descriptive adapter type"""
        raise NotImplementedError()

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        """ The list of supported service types

            The first one is always regarded as the default type.
        """
        raise NotImplementedError()

    @classmethod
    def get_default_service_type(cls) -> ServiceType:
        return cls.get_supported_service_types()[0]

    @property
    def url(self):
        """The base URL to the endpoint"""
        return self._endpoint.url

    def get_current_authenticator(self) -> Optional[Authenticator]:
        return HttpAuthenticatorFactory.create_multiple_from(endpoint=self._endpoint)[0] \
            if self.require_authentication() \
            else None

    def require_authentication(self) -> bool:
        return len(self._endpoint.get_authentications()) > 0

    def create_http_session(self, suppress_error: bool = True) -> HttpSession:
        """Create HTTP session wrapper"""
        return HttpSession(HttpAuthenticatorFactory.create_multiple_from(endpoint=self._endpoint),
                           suppress_error=suppress_error)

    @classmethod
    def make(cls, endpoint: ServiceEndpoint):
        """Create this class with the given `endpoint`."""
        if not endpoint.type:
            endpoint.type = cls.get_default_service_type()

        return cls(endpoint)
