"""
OAuth module
"""
import abc
import json
import urllib

import requests

from ..api.model.http_verb import HttpVerb
from ..config.configuration import Configuration
from ..utils.logger import HyperscienceLogging
from .model.credentials import CredentialsBase

logger = HyperscienceLogging().get_logger()
URL_SCHEME = 'https://'


class OAuthInterface(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """
    Interface for OAuth
    """

    def __init__(self, configuration: Configuration) -> None:
        super().__init__()
        self._configuration = configuration

    @abc.abstractmethod
    def login(self, credentials: CredentialsBase) -> str:
        """
        Login to oauth server
        :param credentials: Credentials to be used to authenticate
        :type credentials: CredentialsBase
        :return: authentication cookie to be used with requests
        :rtype: str
        """
        raise NotImplementedError('abstract login is not implemented')


class OAuthService(OAuthInterface):  # pylint: disable=too-few-public-methods
    """
    This handles authentication with oauth
    """

    def login(self, credentials: CredentialsBase) -> str:
        response = requests.request(
            HttpVerb.POST.value,
            f'{URL_SCHEME}{self._configuration.auth_server}/api/v1/authn',
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
            data=json.dumps(
                {
                    'username': credentials.decode_client_id(),
                    'password': credentials.decode_client_secret(),
                    'options': {
                        'multiOptionalFactorEnroll': False,
                        'warnBeforePasswordExpired': False,
                    },
                }
            ),
        )
        response.close()
        session_token = json.loads(response.content).get('sessionToken')
        assert session_token, 'Failed to authenticate with okta'
        logger.debug('Successfully logged in to OKTA.')

        response = requests.request(
            HttpVerb.GET.value,
            f'{URL_SCHEME}{self._configuration.hs_domain}/',
            allow_redirects=False,
        )
        new_location = response.headers.get('Location')
        response.close()
        assert new_location, 'Failed to receive authentication location header.'
        logger.debug('Successfully received redirection URL')
        parsed = urllib.parse.urlparse(new_location)

        netloc = parsed.netloc
        response = requests.request(
            HttpVerb.POST.value, f'{URL_SCHEME}{netloc}/api/v1/internal/device/nonce'
        )
        nonce = json.loads(response.content).get('nonce')
        logger.debug('Successfully received nonce.')
        response.close()

        query_str = parsed.query + '&sessionToken=' + session_token + '&nonce=' + nonce
        response = requests.request(
            HttpVerb.GET.value,
            f'{URL_SCHEME}{netloc}{parsed.path}?{query_str}',
            allow_redirects=False,
        )
        response.close()
        redirect = response.headers.get('Location')
        assert redirect, 'Authentication has failed!'
        logger.debug('Successfully authenticated!')
        parsed = urllib.parse.urlparse(redirect)

        response = requests.request(
            HttpVerb.GET.value,
            f'{URL_SCHEME}{self._configuration.hs_domain}/oauth2/idpresponse?{parsed.query}',
            allow_redirects=False,
        )
        response.close()
        cookie = response.headers.get('Set-Cookie')
        assert cookie, 'Cookie is not valid!'
        logger.info('Successfully received cookie! Login is complete.')
        return cookie
