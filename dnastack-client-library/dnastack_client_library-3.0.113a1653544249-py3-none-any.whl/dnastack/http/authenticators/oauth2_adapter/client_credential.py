from typing import Dict, Any, List

import requests

from dnastack.exceptions import AuthException
from dnastack.http.authenticators.oauth2_adapter.abstract import OAuth2Adapter


class ClientCredentialAdapter(OAuth2Adapter):
    __grant_type = 'client_credentials'

    @staticmethod
    def get_expected_auth_info_fields() -> List[str]:
        return [
            'client_id',
            'client_secret',
            'grant_type',
            'resource_url',
            'token_endpoint',
        ]

    def exchange_tokens(self) -> Dict[str, Any]:
        auth_info = self._auth_info
        auth_params = dict(
            client_id=auth_info.client_id,
            client_secret=auth_info.client_secret,
            grant_type=self.__grant_type,
            resource=auth_info.resource_url,
        )

        if auth_info.scope:
            auth_params['scope'] = auth_info.scope

        response = requests.post(auth_info.token_endpoint, params=auth_params)

        if not response.ok:
            raise AuthException()

        return response.json()
