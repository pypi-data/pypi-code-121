import base64
import re
import requests


class NsjAuthenticationService:

    def __init__(self, client_id: str, client_secret: str, introspection_url: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._introspection_url = introspection_url

    def authenticate(self, access_token: str) -> str:
        """
        Check if access_token is valid (throught token introspection endpoint),
        and returns access_token info, or None (is not valid).
        """

        # Checking heaaders
        if not access_token:
            return None

        # Checking format (throught regex)
        matcher = re.compile('^Bearer (.+)$')
        match = matcher.match(access_token)
        if not match:
            return None
        access_token = match.group(1)

        # Calling Introspection Endpoint
        basic = f'{self._client_id}:{self._client_secret}'
        basic = base64.b64encode(basic.encode('utf-8')).decode('utf-8')
        basic = f'Basic {basic}'

        data = {
            'token': access_token,
            'token_type_hint': 'access_token'
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': basic
        }

        resp = requests.post(url=self._introspection_url,
                             data=data, headers=headers, timeout=60)

        if resp.status_code == 401:
            return Exception('Authentication error in token introspection. Check client_id and client_secret.')

        resp.raise_for_status()
        resp = resp.json()

        # Testing result
        if not ('username' in resp):
            return None

        # Returning token info
        return resp
