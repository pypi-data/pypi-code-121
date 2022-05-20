from typing import Optional, Any, Dict
from unittest.mock import patch, MagicMock
from uuid import uuid4

import time
from math import floor
from requests import Response, Request

from dnastack import DataConnectClient
from dnastack.http.session_info import SessionInfo, InMemorySessionStorage, SessionManager, SessionInfoHandler
from dnastack.configuration.models import ServiceEndpoint, ConfigurationModelMixin, OAuth2Authentication
from dnastack.common.environments import env
from dnastack.http.authenticators.abstract import AuthenticationRequired, Authenticator, ReauthenticationRequired, \
    RefreshRequired
from dnastack.http.authenticators.oauth2 import OAuth2Authenticator
from dnastack.http.authenticators.oauth2_adapter.abstract import OAuth2Adapter
from dnastack.http.authenticators.oauth2_adapter.factory import OAuth2AdapterFactory
from ..exam_helper import token_endpoint, client_secret, client_id, \
    authorization_endpoint, personal_access_endpoint, redirect_url, BaseTestCase


class FauxSessionCreator:
    def __init__(self,
                 config_hash: str,
                 expiry_timestamp_delta: int,
                 auth_info: Optional[Dict[str, Any]] = None,
                 refresh_token: Optional[str] = None):
        self.config_hash = config_hash
        self.expiry_timestamp_delta = expiry_timestamp_delta
        self.refresh_token = refresh_token
        self.auth_info = auth_info

    def __call__(self, request_url: Optional[str] = None) -> SessionInfo:
        return self.make(self.config_hash, self.expiry_timestamp_delta, self.auth_info, self.refresh_token)

    @staticmethod
    def make(config_hash: str,
             expiry_timestamp_delta: int,
             auth_info: Optional[Dict[str, Any]] = None,
             refresh_token: Optional[str] = None):
        current_timestamp = floor(time.time())
        return SessionInfo(model_version=4,
                           config_hash=config_hash,
                           access_token='faux_access_token',
                           handler=SessionInfoHandler(auth_info=auth_info) if auth_info else None,
                           refresh_token=refresh_token,
                           token_type='faux_token_type',
                           issued_at=current_timestamp,
                           valid_until=current_timestamp + expiry_timestamp_delta)


class BaseAuthTest(BaseTestCase):
    def _trigger_auth(self, auth: Authenticator):
        request = Request()
        auth.before_request(request)
        self.assertIn('Authorization', request.headers)


class TestOAuth2AuthenticatorUnitTest(BaseAuthTest):
    auth_info = dict(
        type='oauth2',
        client_id='client_id',
        client_secret='client_secret',
        grant_type='client_credentials',
        resource_url='https://foo.io/api/',
        token_endpoint='https://foo.io/auth/token',
    )

    service_endpoint = ServiceEndpoint(
        id='test_endpoint',
        adapter_type='test_adapter',
        url='http://localhost:12345/',
        authentication=auth_info,
    )

    def _mock_adapter_factory(self, token_exchange_response: Dict[str, Any]):
        mock_adapter = MagicMock(OAuth2Adapter)
        mock_adapter.check_config_readiness.return_value = True
        mock_adapter.exchange_tokens.return_value = token_exchange_response

        mock_adapter_factory = MagicMock(OAuth2AdapterFactory)
        mock_adapter_factory.get_from.return_value = mock_adapter

        return mock_adapter_factory

    def test_authorizer_authorize_first_time(self):
        session_storage = InMemorySessionStorage()
        session_manager = SessionManager(session_storage)

        mock_adapter_factory = self._mock_adapter_factory(dict(
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_type='test_token_type',
            expires_in=60,
        ))

        auth = OAuth2Authenticator(self.service_endpoint, self.auth_info, session_manager, mock_adapter_factory)
        with self.assertRaises(AuthenticationRequired):
            auth._restore_session()

        self._trigger_auth(auth)

        current_session = auth._restore_session()

        self.assertIsNotNone(current_session)
        self.assertIsNotNone(current_session.handler)
        for auth_info_key, expected_auth_info_value in self.auth_info.items():
            self.assertEqual(current_session.handler.auth_info[auth_info_key],
                             expected_auth_info_value,
                             f'AuthInfo/{auth_info_key} is not matched')
        self.assertGreater(current_session.valid_until, time.time())
        self.assertTrue(current_session.is_valid())

    def test_authorizer_handles_auth_info_update_with_reauthorization(self):
        session_with_old_config = FauxSessionCreator.make('old_config_hash', 60)

        session_storage = InMemorySessionStorage()
        session_storage[OAuth2Authentication(**self.auth_info).get_content_hash()] = session_with_old_config

        session_manager = SessionManager(session_storage)

        mock_adapter_factory = self._mock_adapter_factory(dict(
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_type='test_token_type',
            expires_in=60,
        ))

        auth = OAuth2Authenticator(self.service_endpoint, self.auth_info, session_manager, mock_adapter_factory)

        with self.assertRaises(ReauthenticationRequired):
            # noinspection PyStatementEffect
            auth._restore_session()

        self._trigger_auth(auth)

        current_session = auth._restore_session()

        self.assertIsNotNone(current_session)
        self.assertIsNotNone(current_session.handler)
        for auth_info_key, expected_auth_info_value in self.auth_info.items():
            self.assertEqual(current_session.handler.auth_info[auth_info_key],
                             expected_auth_info_value,
                             f'AuthInfo/{auth_info_key} is not matched')
        self.assertNotEqual(current_session, session_with_old_config)
        self.assertTrue(current_session.is_valid())

    def test_authorizer_handles_stale_session_with_reauthorization(self):
        stale_session = FauxSessionCreator.make(ConfigurationModelMixin.hash(self.auth_info), -60)

        session_storage = InMemorySessionStorage()
        session_storage[OAuth2Authentication(**self.auth_info).get_content_hash()] = stale_session

        session_manager = SessionManager(session_storage)

        mock_adapter_factory = self._mock_adapter_factory(dict(
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_type='test_token_type',
            expires_in=60,
        ))

        auth = OAuth2Authenticator(self.service_endpoint, self.auth_info, session_manager, mock_adapter_factory)

        with self.assertRaises(ReauthenticationRequired):
            # noinspection PyStatementEffect
            auth._restore_session()

        self._trigger_auth(auth)

        current_session = auth._restore_session()

        self.assertIsNotNone(current_session)
        self.assertNotEqual(current_session, stale_session)
        self.assertGreater(current_session.valid_until, stale_session.valid_until)
        self.assertTrue(current_session.is_valid())
        self.assertFalse(stale_session.is_valid())

    def test_authorizer_handles_stale_session_with_token_refresh(self):
        stale_session = FauxSessionCreator.make(ConfigurationModelMixin.hash(self.auth_info), -60,
                                                self.auth_info,
                                                'faux_refresh_token_1')

        session_storage = InMemorySessionStorage()
        session_storage[OAuth2Authentication(**self.auth_info).get_content_hash()] = stale_session

        session_manager = SessionManager(session_storage)

        auth = OAuth2Authenticator(self.service_endpoint, self.auth_info, session_manager)

        with self.assertRaises(RefreshRequired):
            # noinspection PyStatementEffect
            auth._restore_session()

        with patch('requests.post') as mock_post_method:
            mock_response = MagicMock(Response)
            mock_response.ok = True
            mock_response.json.return_value = dict(
                access_token='fake_access_token',
                refresh_token='fake_refresh_token',
                token_type='fake_token_type',
                expires_in=100,
            )

            mock_post_method.return_value = mock_response

            auth.refresh()

        current_session = auth._restore_session()

        self.assertIsNotNone(current_session)
        self.assertNotEqual(current_session, stale_session)
        self.assertGreater(current_session.valid_until, stale_session.valid_until)
        self.assertTrue(current_session.is_valid())
        self.assertFalse(stale_session.is_valid())


class TestOAuth2AuthenticatorEndToEnd(BaseAuthTest):
    """
    Test authentication flows

    .. note:: The URL used in the authorization tests are fake.
    """

    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL',
                            default='https://collection-service.viral.ai/data-connect/')

    def test_client_credentials_flow(self):
        test_endpoint = self.__create_endpoint(dict(
            type='oauth2',
            client_id=client_id,
            client_secret=client_secret,
            grant_type='client_credentials',
            resource_url=self.test_resource_url,
            token_endpoint=token_endpoint,
        ))

        auth = OAuth2Authenticator(test_endpoint, test_endpoint.authentication)

        self._trigger_auth(auth)

        auth_session = auth._restore_session()
        self.assertIsNotNone(auth_session)
        self.assertIsNotNone(auth_session.config_hash)
        self.assert_not_empty(auth_session.access_token, 'empty access token')
        self.assertIsNone(auth_session.refresh_token, 'non-empty refresh token')
        self.assertGreater(auth_session.valid_until, 0)

        if auth_session.model_version == 3:
            self.assertIsNone(auth_session.handler)
        elif auth_session.model_version == 4:
            self.assertIsInstance(auth_session.handler, SessionInfoHandler)

        # As the OAuth server may respond too quickly, this is to ensure that the expiry times are different.
        time.sleep(1)

        # Reauthorize the endpoint with updated config
        test_endpoint.authentication['redirect_url'] = 'https://dnastack.com/'

        self._trigger_auth(auth)

        refreshed_auth_session = auth._restore_session()
        self.assertIsNotNone(refreshed_auth_session)
        self.assertIsNotNone(refreshed_auth_session.config_hash)
        self.assert_not_empty(refreshed_auth_session.access_token, 'empty access token')
        self.assertIsNone(refreshed_auth_session.refresh_token, 'non-empty refresh token')
        self.assertGreater(refreshed_auth_session.valid_until, 0)

        # Check that the session has been refreshed when the auth info is updated.
        self._deep_assert_not_equal(refreshed_auth_session, auth_session)
        self.assertNotEqual(refreshed_auth_session.config_hash, auth_session.config_hash)
        self.assertNotEqual(refreshed_auth_session.access_token, auth_session.access_token)
        self.assertGreater(refreshed_auth_session.valid_until, auth_session.valid_until)

    def _deep_assert_not_equal(self, a, b):
        try:
            self.assertNotEqual(a, b)
        except AssertionError:
            import pprint
            pprint.pprint(
                {
                    'a': a.dict(),
                    'b': b.dict(),
                }, indent=4
            )

            for p_name in dir(a):
                if p_name[0] == '_' or callable(getattr(a, p_name)):
                    continue
                self.assertNotEqual(getattr(a, p_name),
                                    getattr(b, p_name),
                                    f'{type(a).__name__}.{p_name} is unexpectedly the same')

    def test_personal_access_token_flow(self):
        email = env('E2E_AUTH_PAT_TEST_EMAIL')
        token = env('E2E_AUTH_PAT_TEST_TOKEN')

        if not email or not token:
            self.skipTest('The PAT flow test does not have both email and token.')

        test_endpoint = self.__create_endpoint(dict(
            type='oauth2',
            authorization_endpoint=authorization_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            grant_type='authorization_code',
            personal_access_endpoint=personal_access_endpoint,
            personal_access_email=email,
            personal_access_token=token,
            redirect_url=redirect_url,
            resource_url=self.test_resource_url,
            token_endpoint=token_endpoint,
        ))

        auth = OAuth2Authenticator(test_endpoint, test_endpoint.authentication)

        self._trigger_auth(auth)

        auth_session = auth._restore_session()
        self.assertIsNotNone(auth_session)
        self.assert_not_empty(auth_session.access_token, 'empty access token')
        self.assertGreater(auth_session.valid_until, 0)

    def __create_endpoint(self, authentication: Dict[str, Any]) -> ServiceEndpoint:
        return ServiceEndpoint(
            id=f'auto-test-{uuid4()}',
            adapter_type=DataConnectClient.get_adapter_type(),
            url=self.test_resource_url,
            authentication=authentication,
        )
