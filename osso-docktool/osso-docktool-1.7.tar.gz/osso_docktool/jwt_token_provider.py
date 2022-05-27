from time import time
import base64
import json

import requests

try:
    from urllib.parse import urljoin, urlparse, parse_qs  # py3
except ImportError:
    from urlparse import urljoin, urlparse, parse_qs  # py2

from . import settings


def base64_decode(value):
    return base64.b64decode(value + '=' * (-len(value) % 4))


def get_expiry(jwt_token):
    payload = json.loads(
        base64_decode(jwt_token.split('.')[1]).decode('ascii'))
    exp = payload.get('exp', 0)
    return int(exp - time())


def is_expired(jwt_token):
    return ((get_expiry(jwt_token) - 10) < 0)


class JWTTokenProvider(object):
    authserver_token_path = '/api/user/token/'

    def __init__(self, login_url_or_auth_scheme_url):
        # Either SERVER/api/auth/scheme/ or SERVER/api-auth/login/.
        self._first_url = login_url_or_auth_scheme_url
        self.client = requests.session()

    def get_authorize_url(self):
        res = self.client.get(self._first_url, allow_redirects=False)
        if 300 <= res.status_code < 400:
            # https://AUTHSERVER/openid/authorize?scope=openid+profile&'
            #   redirect_uri=REDIR_URI&response_type=code&client_id=CLIENT_CODE
            location = res.headers.get('Location')
            if 'response_type=code' in location:
                return location
        elif res.status_code == 200:
            # {"data":{"authorizeUrl":"LOCATION_AS_SEEN_ABOVE"},
            # "type":"oidc","name":"oidc"}
            data = res.json()
            if data['type'] == 'oidc':
                return data['data']['authorizeUrl']
        raise ValueError('Unknown scheme {} -> {} {!r}'.format(
            self._first_url, res.status_code, res.text))

    def get_token_url(self):
        # We don't seem to need scope. Just use the client_id.
        url = self.get_authorize_url()
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        client_id = qs.get('client_id')
        assert len(client_id) == 1 and client_id[0], url
        return '{}?client_id={}'.format(
            # urljoin chops off the original query_string.
            urljoin(parsed.geturl(), self.authserver_token_path), client_id[0])

    def get_jwt_token(self, auth_token=None):
        url = self.get_token_url()

        if auth_token:
            headers = {'Authorization': 'Token {}'.format(auth_token)}
            kwargs = {'headers': headers}
        else:
            raise NotImplementedError()

        res = self.client.get(url, **kwargs)
        if res.status_code != 200:
            raise ValueError('Bad token response {} -> {} {!r}'.format(
                url, res.status_code, res.text))
        js = res.json()
        assert js.get('token_type') == 'Bearer', (url, js)
        return js['id_token']


def get_jwt_token(scheme_url, auth_token):
    prov = JWTTokenProvider(scheme_url)
    return prov.get_jwt_token(auth_token=auth_token)


def main():
    prov = JWTTokenProvider(settings.DASHBOARD_SCHEME_URL)
    jwt = prov.get_jwt_token(auth_token=settings.DASHBOARD_AUTH_TOKEN)
    print('Got JWT')
    print(jwt)
    print('Expires in {}s'.format(get_expiry(jwt)))


if __name__ == '__main__':
    main()
