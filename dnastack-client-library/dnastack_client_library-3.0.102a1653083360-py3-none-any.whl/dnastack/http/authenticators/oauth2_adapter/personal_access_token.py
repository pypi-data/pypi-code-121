from typing import Any, Dict, List
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup
from time import sleep

from dnastack.exceptions import LoginException
from dnastack.feature_flags import in_global_debug_mode
from dnastack.http.authenticators.oauth2_adapter.abstract import OAuth2Adapter


class PersonalAccessTokenAdapter(OAuth2Adapter):
    """
    Adapter for authentication with DNAstack's personal access token
    """
    @staticmethod
    def get_expected_auth_info_fields() -> List[str]:
        return [
            'authorization_endpoint',
            'client_id',
            'client_secret',
            'grant_type',
            'personal_access_endpoint',
            'personal_access_email',
            'personal_access_token',
            'redirect_url',
            'resource_url',
            'token_endpoint',
        ]

    def exchange_tokens(self) -> Dict[str, Any]:
        session = requests.Session()

        info = self._auth_info

        self._logger.debug(f'Authenticating with PAT...')

        login_params = dict(token=info.personal_access_token,
                            email=info.personal_access_email)

        if in_global_debug_mode:
            self._logger.debug(f'login_params = {login_params}')

        login_url = info.personal_access_endpoint
        login_res = session.get(login_url,
                                params=dict(token=info.personal_access_token,
                                            email=info.personal_access_email),
                                allow_redirects=False)

        if not login_res.ok:
            session.close()
            raise LoginException(login_url, "The personal access token and/or email provided is invalid")

        self._logger.debug(f'Making an auth code challenge...')
        auth_code_url = info.authorization_endpoint
        auth_code_params = {
            "response_type": "code",
            "client_id": info.client_id,
            "resource": info.resource_url,
            "redirect_uri": info.redirect_url,
        }

        if info.scope:
            auth_code_params['scope'] = info.scope

        if in_global_debug_mode:
            self._logger.debug(f'auth_code_params = {auth_code_params}')

        auth_code_res = session.get(info.authorization_endpoint, params=auth_code_params, allow_redirects=False)

        auth_code_redirect_url = auth_code_res.headers["Location"]
        if "Location" in auth_code_res.headers:
            parsed_auth_code_redirect_url = urlparse(auth_code_redirect_url)
        else:
            session.close()
            raise LoginException(url=auth_code_url, msg="Authorization failed")

        query_params = parse_qs(parsed_auth_code_redirect_url.query)
        auth_code = self.__extract_code(auth_code_redirect_url)
        if parsed_auth_code_redirect_url.path.startswith('/oauth/confirm_access'):
            # Wait for a few seconds to give a chance to the user to abort the pre-authorization process.
            self._logger.warning('The access has not been authorized. Will automatically attempt to pre-authorize the '
                                 'access in 10 seconds.\n\nYou may press CTRL+C to abort the process')
            try:
                sleep(10)
            except KeyboardInterrupt:
                raise LoginException(url=auth_code_url, msg='User aborted the authentication process')
            confirm_prompt_response = session.get(auth_code_redirect_url)

            # Automatically authorize the access
            doc = BeautifulSoup(confirm_prompt_response.text, features="html.parser")
            form_element = [f for f in doc.find_all('form') if f.get('action').startswith('/oauth/confirm_access')][0]
            confirm_url: str = form_element.get('action')
            if not confirm_url.startswith('https://'):
                confirm_url = urljoin(info.token_endpoint, confirm_url)
            inputs = {
                input_element.get('name'): input_element.get('value')
                for input_element in form_element.find_all('input')
            }

            # Initiate the access confirmation response
            confirm_response = session.post(confirm_url, params=inputs, allow_redirects=False)
            if "Location" in confirm_response.headers:
                post_confirm_redirect_url = confirm_response.headers['Location']
            else:
                session.close()
                raise LoginException(url=auth_code_url, msg="Authorization failed (access confirmation failure)")

            post_confirm_code = self.__extract_code(post_confirm_redirect_url)
            if post_confirm_code:
                auth_code = query_params["code"][0]
            else:
                session.close()
                raise LoginException(url=auth_code_url, msg="Authorization failed (after access confirmation)")
        elif auth_code is None:
            session.close()
            raise LoginException(url=auth_code_url, msg="Authorization failed (no access confirmation)")

        self._logger.debug(f'Making a token exchange...')

        token_url = info.token_endpoint

        authorization_code_params = {
            "grant_type": info.grant_type,
            "code": auth_code,
            "resource": info.resource_url,
            "client_id": info.client_id,
            "client_secret": info.client_secret,
        }

        if info.scope:
            authorization_code_params['scope'] = info.scope

        if in_global_debug_mode:
            self._logger.debug(f'authorization_code_params = {authorization_code_params}')

        auth_token_res = requests.post(token_url, data=authorization_code_params)
        auth_token_json = auth_token_res.json()

        if in_global_debug_mode:
            self._logger.debug(f'Done: {auth_token_res.text}')

        session.close()

        if not auth_token_res.ok:
            raise LoginException(token_url, "Failed to get a token from the token endpoint")

        return auth_token_json

    @staticmethod
    def __extract_code(url: str):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params and query_params["code"]:
            return query_params["code"][0]
        else:
            return None