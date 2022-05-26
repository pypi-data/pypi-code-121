from copy import deepcopy
from json import JSONDecodeError

import requests
from imagination import container
from requests import Request, Session, Response
from time import time
from typing import Optional, Any, Dict, Union

from dnastack.common.logger import get_logger
from dnastack.configuration.models import ServiceEndpoint, OAuth2Authentication, ConfigurationModelMixin
from dnastack.feature_flags import in_global_debug_mode
from dnastack.http.authenticators.abstract import Authenticator, AuthenticationRequired, ReauthenticationRequired, \
    RefreshRequired, InvalidStateError, NoRefreshToken, AuthState, ReauthenticationRequiredDueToConfigChange, \
    AuthStateStatus
from dnastack.http.authenticators.oauth2_adapter.factory import OAuth2AdapterFactory
from dnastack.http.session_info import SessionInfo, SessionManager, SessionInfoHandler


class OAuth2MisconfigurationError(RuntimeError):
    pass


class OAuth2Authenticator(Authenticator):
    def __init__(self,
                 endpoint: ServiceEndpoint,
                 auth_info: Dict[str, Any],
                 session_manager: Optional[SessionManager] = None,
                 adapter_factory: Optional[OAuth2AdapterFactory] = None):
        super().__init__()

        self._endpoint = endpoint
        self._auth_info = auth_info
        self._logger = get_logger(f'E/{endpoint.type}/{endpoint.id}'
                                  if endpoint
                                  else f'A/{self.session_id}')
        self._adapter_factory: OAuth2AdapterFactory = adapter_factory or container.get(OAuth2AdapterFactory)
        self._session_manager: SessionManager = session_manager or container.get(SessionManager)
        self._session_info: Optional[SessionInfo] = None

    @property
    def session_id(self):
        return OAuth2Authentication(**self._auth_info).get_content_hash()

    def get_state(self) -> AuthState:
        status = AuthStateStatus.READY
        grants: Dict[str, Any] = dict()

        try:
            session = self.restore_session()
            grants['scope'] = session.scope
            grants['refresh_token'] = session.refresh_token
        except RefreshRequired:
            status = 'require-refresh'
        except AuthenticationRequired:
            status = 'uninitialized'
        except ReauthenticationRequiredDueToConfigChange:
            status = 'require-reauthentication/config-changed'
        except ReauthenticationRequired:
            status = 'require-reauthentication/expired'

        return AuthState(
            authenticator=self.fully_qualified_class_name,
            id=self.session_id,
            auth_info=deepcopy(self._auth_info),
            grants=grants,
            status=status,
        )

    def authenticate(self) -> SessionInfo:
        self._logger.debug('Initiate the authorization process')

        auth_info = OAuth2Authentication(**self._auth_info)

        adapter = self._adapter_factory.get_from(auth_info)

        if not adapter:
            raise OAuth2MisconfigurationError('Cannot determine the type of authentication '
                                              f'({auth_info.json(sort_keys=True, exclude_none=True)})')

        adapter.check_config_readiness()

        raw_response = adapter.exchange_tokens()

        self._session_info = self._convert_token_response_to_session(
            auth_info.dict(),
            raw_response
        )

        self._session_manager.save(auth_info.get_content_hash(), self._session_info)

        return self._session_info

    def refresh(self) -> SessionInfo:
        session_info = self._session_info or self._session_manager.restore(self.session_id)

        if session_info.model_version < 4:
            raise ReauthenticationRequired(
                'The stored session information does not provide enough information to refresh token.')

        if not session_info.refresh_token:
            raise NoRefreshToken()

        auth_info = OAuth2Authentication(**session_info.handler.auth_info)
        refresh_token = session_info.refresh_token
        refresh_token_res: Optional[Response] = None

        try:
            refresh_token_res = requests.post(
                auth_info.token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": session_info.scope,
                },
                auth=(auth_info.client_id, auth_info.client_secret),
            )

            if refresh_token_res.ok:
                refresh_token_json = refresh_token_res.json()

                if in_global_debug_mode:
                    self._logger.debug(f'refresh_token_json = {refresh_token_json}')

                # Fill in the missing data.
                refresh_token_json['refresh_token'] = refresh_token

                # Update the session
                self._session_info = self._convert_token_response_to_session(auth_info.dict(), refresh_token_json)

                self._session_manager.save(auth_info.get_content_hash(), self._session_info)

                return self._session_info
            else:
                error_msg = f"Unable to refresh tokens"

                try:
                    error_json = refresh_token_res.json()
                    error_msg += f": {error_json['error_description']}"
                except JSONDecodeError:
                    pass

                self._logger.error(error_msg)

                raise InvalidStateError(error_msg)
        finally:
            if refresh_token_res:
                refresh_token_res.close()

    def revoke(self):
        # Clear the local cache
        self._session_info = None
        self._session_manager.delete(self.session_id)

    def restore_session(self) -> Optional[SessionInfo]:
        current_auth_info = OAuth2Authentication(**self._auth_info)
        session = self._session_info or self._session_manager.restore(self.session_id)

        if not session:
            raise AuthenticationRequired('No session available')
        elif session.is_valid():
            current_config_hash = current_auth_info.get_content_hash()
            stored_config_hash = session.config_hash

            if current_config_hash == stored_config_hash:
                return session
            else:
                raise ReauthenticationRequiredDueToConfigChange(
                    'The session is invalidated as the endpoint configuration has changed.'
                )
        else:
            if session.refresh_token:
                raise RefreshRequired()
            else:
                raise ReauthenticationRequired('The session is invalid and refreshing tokens is not possible.')

    def _convert_token_response_to_session(self,
                                           authentication: Dict[str, Any],
                                           response: Dict[str, Any]):
        assert 'access_token' in response, f'Failed to exchange tokens due to an unexpected response ({response})'

        created_time = time()
        expiry_time = created_time + response['expires_in']

        current_auth_info = OAuth2Authentication(**self._auth_info)

        return SessionInfo(
            model_version=4,
            config_hash=current_auth_info.get_content_hash(),
            access_token=response['access_token'],
            refresh_token=response.get('refresh_token'),
            scope=response.get('scope'),
            token_type=response['token_type'],
            issued_at=created_time,
            valid_until=expiry_time,
            handler=SessionInfoHandler(auth_info=authentication)
        )

    def update_request(self, session: SessionInfo, r: Union[Request, Session]) -> Union[Request, Session]:
        r.headers["Authorization"] = f"Bearer {session.access_token}"
        return r

    @classmethod
    def make(cls, endpoint: ServiceEndpoint, auth_info: Dict[str, Any]):
        return cls(endpoint, auth_info)
