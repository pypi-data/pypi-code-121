from contextlib import contextmanager

import click
from imagination import container
from typing import List, Optional, Any, Dict, Iterator

from dnastack.helpers.client_factory import ConfigurationBasedClientFactory
from ..exporter import display_result_iterator
from ..utils import command, ArgumentSpec, echo_header
from ...client.base_client import BaseServiceClient
from ...common.logger import get_logger
from ...common.simple_stream import SimpleStream
from ...configuration.manager import ConfigurationManager
from ...configuration.models import ServiceEndpoint, ConfigurationModelMixin
from ...exceptions import LoginException
from ...http.authenticators.abstract import Authenticator, AuthenticationRequired, ReauthenticationRequired, \
    RefreshRequired, AuthStateStatus
from ...http.authenticators.factory import HttpAuthenticatorFactory
from ...http.authenticators.oauth2 import OAuth2Authenticator


@click.group("auth")
def auth():
    """ Manage authentication and authorization """


def _get_client(adapter_type: str) -> BaseServiceClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    client_class = factory.get_client_class(adapter_type)
    client = factory.get(client_class)

    if not client:
        raise LoginException(msg="There is no configured service")
    elif not client.require_authentication():
        raise LoginException(msg="The authentication information is not defined")
    return client


@command(
    auth,
    specs=[
        ArgumentSpec(name='revoke_existing',
                     help='If used, the existing session will be automatically revoked before the re-authentication'),
    ],
)
def login(endpoint_id: Optional[str] = None, revoke_existing: bool = False):
    """
    Log in to ALL service endpoints or ONE specific service endpoint

    For examples:

        dnastack auth login --endpoint-id

    """
    handler = AuthCommandHandler()
    handler.initiate_authentications(endpoint_ids=[endpoint_id] if endpoint_id else [], revoke_existing=revoke_existing)


@command(auth)
def status():
    """ Check the status of all authenticator """
    handler = AuthCommandHandler()

    display_result_iterator(handler.get_states())


class AuthCommandHandler:
    def __init__(self):
        self._logger = get_logger(type(self).__name__)
        self._config_manager: ConfigurationManager = container.get(ConfigurationManager)

    def get_states(self) -> Iterator[Dict[str, Any]]:
        endpoints = self._get_filtered_endpoints()
        for authenticator in self.get_authenticators():
            auth_state = authenticator.get_state()
            state = auth_state.dict()

            # Simplify the auth/session info
            state['auth_info'] = self._remove_none_entry_from(auth_state.auth_info)
            current_hash = ConfigurationModelMixin.hash(state['auth_info'])

            # Retrieve the associated endpoints.
            state['endpoints'] = []
            for endpoint in endpoints:
                for auth_info in endpoint.get_authentications():
                    ref_hash = ConfigurationModelMixin.hash(self._remove_none_entry_from(auth_info))
                    if ref_hash == current_hash:
                        state['endpoints'].append(endpoint.id)

            yield state

    def _remove_none_entry_from(self, d: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in d.items()
            if v is not None
        }

    def initiate_authentications(self, endpoint_ids: List[str] = None, revoke_existing: bool = False):
        authenticators = self.get_authenticators(endpoint_ids)
        with click.progressbar(authenticators, label='Authentication', show_eta=False, show_percent=True) as bar:
            for authenticator in bar:
                print()

                # NOTE: This is designed exclusively for OAuth2 process. Need to rework to support other types of authenticators.
                state = authenticator.get_state()

                url = state.auth_info.get('resource_url')
                client_id = state.auth_info.get('client_id')
                auth_scope = state.auth_info.get('scope')

                if state.status == AuthStateStatus.READY:
                    echo_header(f'The client with ID "{client_id}" for "{url}" has already been authorized.', bg='green')

                    granted_scope = state.grants.get('scope')

                    if granted_scope:
                        parsed_scopes = sorted(granted_scope.split(r' '))
                        click.secho(f'Here is the list of authorized scope{"s" if len(parsed_scopes) != 1 else ""}:')
                        for parsed_scope in parsed_scopes:
                            click.secho(f' - {parsed_scope}')
                        print()

                    continue

                echo_header(f'Authenticating the client with ID "{client_id}" for {url}...')

                if auth_scope:
                    parsed_scopes = sorted(auth_scope.split(r' '))
                    click.secho(f'Here is the list of requesting scope{"s" if len(parsed_scopes) != 1 else ""}:', dim=True)
                    for parsed_scope in parsed_scopes:
                        click.secho(f' - {parsed_scope}', dim=True)

                if revoke_existing:
                    with self._show_step(f'Revoking existing session... ', 'done', 'blue'):
                        authenticator.revoke()

                with self._show_step('Authenticating...', 'ok', 'green'):
                    print()
                    authenticator.initialize()
                print()

    @contextmanager
    def _show_step(self, message: str, post_op_message: str, color: str):
        click.secho(message, dim=True)
        try:
            yield
        except KeyboardInterrupt:
            click.secho(message + ' ', dim=True, nl=False)
            click.secho('SKIPPED', fg='yellow')
        else:
            click.secho(message + ' ', dim=True, nl=False)
            click.secho(post_op_message.upper(), fg=color)

    def get_authenticators(self, endpoint_ids: List[str] = None) -> List[Authenticator]:
        filtered_endpoints = self._get_filtered_endpoints(endpoint_ids)
        return HttpAuthenticatorFactory.create_multiple_from(endpoints=filtered_endpoints)

    def _get_filtered_endpoints(self, endpoint_ids: List[str] = None) -> List[ServiceEndpoint]:
        return [
            endpoint
            for endpoint in self._config_manager.load().endpoints
            if not endpoint_ids or endpoint.id in endpoint_ids
        ]
