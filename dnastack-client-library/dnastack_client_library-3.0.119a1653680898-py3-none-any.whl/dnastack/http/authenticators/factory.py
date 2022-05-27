from typing import List, Any, Dict, Optional

from dnastack.configuration.models import ServiceEndpoint, OAuth2Authentication, ConfigurationModelMixin
from dnastack.http.authenticators.abstract import Authenticator
from dnastack.http.authenticators.oauth2 import OAuth2Authenticator


class UnsupportedAuthenticationInformationError(RuntimeError):
    pass


class HttpAuthenticatorFactory:
    @staticmethod
    def create_multiple_from(endpoint: Optional[ServiceEndpoint] = None,
                             endpoints: Optional[List[ServiceEndpoint]] = None) -> List[Authenticator]:
        iterating_endpoints: List[ServiceEndpoint] = []

        if endpoint:
            iterating_endpoints.append(endpoint)

        if endpoints:
            iterating_endpoints.extend(endpoints)

        return [
            OAuth2Authenticator.make(endpoint, HttpAuthenticatorFactory._parse_auth_info(auth_info))
            for auth_info in HttpAuthenticatorFactory.get_unique_auth_info_list(iterating_endpoints)
        ]

    @staticmethod
    def _parse_auth_info(auth_info: Dict[str, Any]) -> Dict[str, Any]:
        auth_type = auth_info.get('type') or 'oauth2'
        if auth_type == 'oauth2':
            # Use the model to validate the configuration.
            config = OAuth2Authentication(**auth_info)

            # NOTE: Should raise a custom exception if it fails the model validation.

            return config.dict()
        else:
            raise UnsupportedAuthenticationInformationError(auth_info)

    @staticmethod
    def get_unique_auth_info_list(endpoints: List[ServiceEndpoint]) -> List[Dict[str, Any]]:
        unique_auth_info_map: Dict[str, Dict[str, Any]] = dict()

        for endpoint in endpoints:
            for auth_info in endpoint.get_authentications():
                unique_auth_info_map[ConfigurationModelMixin.hash(auth_info)] = auth_info

        return sorted(unique_auth_info_map.values(), key=lambda a: a.get('resource_url') or a.get('type'))
