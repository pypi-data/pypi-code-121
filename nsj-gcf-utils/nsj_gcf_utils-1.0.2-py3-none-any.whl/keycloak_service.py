from typing import Tuple

from nsj_gcf_utils.http_util import HttpUtil


class KeycloackService:
    """
    Class to authentication with KeyCloak.
    """
    _keycloack_token_url: str

    def __init__(self, keycloack_token_url: str) -> None:
        self._keycloack_token_url = keycloack_token_url

    # TODO Melhorar controle de conexão, incluindo renovação do acess_token pelo refresh_token

    def authenticate(self, client_id: str, username: str, password: str, scope: str, client_secret: str = None) -> Tuple[str, int, str, int]:
        """
        Authenticate with keycloak.

        Returns a tuple, with:
        [access_token: str, expires_in: int, refresh_token: str, refresh_expires_in: int]
        """

        # Making data
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': client_id,
            'scope': scope,
            'grant_type': 'password',
            'username': username,
            'password': password
        }

        if client_secret is not None:
            data['client_secret'] = client_secret

        # Calling API
        resp = HttpUtil.post_retry(self._keycloack_token_url,
                                   headers=headers, data=data, format_data=False, resouce_description='get_access_token')

        # Reading result
        resp = resp.json()

        return (
            resp['access_token'],
            resp['expires_in'],
            resp['refresh_token'],
            resp['refresh_expires_in']
        )
