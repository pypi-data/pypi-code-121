from typing import List, Any, Dict

from dnastack.configuration.models import ServiceEndpoint, OAuth2Authentication
from dnastack.http.authenticators.abstract import Authenticator
from dnastack.http.authenticators.oauth2 import OAuth2Authenticator


class UnsupportedAuthenticationInformationError(RuntimeError):
    pass


class HttpAuthenticatorFactory:
    @staticmethod
    def create_multiple_from(endpoint: ServiceEndpoint) -> List[Authenticator]:
        return [
            OAuth2Authenticator.make(endpoint,
                                     HttpAuthenticatorFactory._parse_auth_info(auth_info))
            for auth_info in endpoint.get_authentications()
        ]

    @staticmethod
    def _parse_auth_info(auth_info: Dict[str, Any]) -> Dict[str, Any]:
        auth_type = auth_info.get('type') or 'oauth2'
        if auth_type == 'oauth2':
            # Use the model to validate the configuration.
            config = OAuth2Authentication(**auth_info)

            # TODO raised an exception if it fails the model validation.

            return config.dict()
        else:
            raise UnsupportedAuthenticationInformationError(auth_info)
