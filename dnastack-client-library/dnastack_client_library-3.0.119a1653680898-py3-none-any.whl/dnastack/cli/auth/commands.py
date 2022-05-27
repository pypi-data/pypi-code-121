import click
from imagination import container
from typing import List, Optional, Any, Dict, Iterator

from dnastack.helpers.client_factory import ConfigurationBasedClientFactory
from ..exporter import display_result_iterator
from ..utils import command, ArgumentSpec, echo_header, echo_list, echo_progress
from ...common.logger import get_logger
from ...configuration.manager import ConfigurationManager
from ...configuration.models import ServiceEndpoint, ConfigurationModelMixin
from ...http.authenticators.abstract import Authenticator, AuthStateStatus
from ...http.authenticators.factory import HttpAuthenticatorFactory


@click.group("auth")
def auth():
    """ Manage authentication and authorization """


@command(
    auth,
    specs=[
        ArgumentSpec(name='revoke_existing',
                     help='If used, the existing session will be automatically revoked before the re-authentication'),
    ],
)
def login(endpoint_id: Optional[str] = None, revoke_existing: bool = False):
    """
    Log in to ALL service endpoints or ONE specific service endpoint.

    If the endpoint ID is not specified, it will initiate the auth process for all endpoints.
    """
    handler = AuthCommandHandler()
    handler.initiate_authentications(endpoint_ids=[endpoint_id] if endpoint_id else [], revoke_existing=revoke_existing)


@command(auth)
def status():
    """ Check the status of all authenticators. """
    handler = AuthCommandHandler()
    display_result_iterator(handler.get_states())


@command(auth,
         specs=[
             ArgumentSpec(
                 name='force',
                 help='Force the auth revocation without prompting the user for confirmation',
             )
         ])
def revoke(endpoint_id: Optional[str] = None, force: bool = False):
    """
    Revoke the authorization to one to many endpoints.

    If the endpoint ID is not specified, it will revoke all authorizations.
    """
    handler = AuthCommandHandler()
    handler.revoke([endpoint_id] if endpoint_id else [], force)


class AuthCommandHandler:
    _status_color_map = {
        AuthStateStatus.READY: 'green',
        AuthStateStatus.UNINITIALIZED: 'magenta',
        AuthStateStatus.REFRESH_REQUIRED: 'yellow',
        AuthStateStatus.REAUTH_REQUIRED: 'red',
    }

    def __init__(self):
        self._logger = get_logger(type(self).__name__)
        self._config_manager: ConfigurationManager = container.get(ConfigurationManager)
        self._client_factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)

    def revoke(self, endpoint_ids: List[str], no_confirmation: bool):
        # NOTE: This is currently designed exclusively to work with OAuth2 config.
        #       Need to rework (on the output) to support other types of authenticators.

        if not no_confirmation and not endpoint_ids:
            echo_header('WARNING: You are about to revoke the access to all endpoints.', bg='yellow', fg='white')

        states = list(self.get_states(endpoint_ids))
        endpoint_ids_with_access_removed: List[str] = []

        for authenticator in self.get_authenticators(endpoint_ids):
            state = [s for s in states if s['id'] == authenticator.session_id][0]
            status = state['status']
            client_id = state['auth_info']['client_id']
            resource_url = state['auth_info']['resource_url']

            affected_endpoint_ids = [
                f'{endpoint_id} (requested)' if endpoint_id in endpoint_ids else endpoint_id
                for endpoint_id in state['endpoints']
            ]

            color_code = self._status_color_map[status]

            echo_header(f'Client ID: {client_id}\nResource URL: {resource_url}')

            click.secho('Status: ', nl=False)
            click.secho(status.upper(), fg=color_code)

            if state.get('grants') and state.get('grants').get('scope'):
                granted_scopes = sorted(str(state.get('grants').get('scope')).split(r' '))
                echo_list('Granted scope(s):', granted_scopes)

            echo_list('Affected endpoint(s):', affected_endpoint_ids)

            print()

            if status == AuthStateStatus.UNINITIALIZED:
                click.secho('The client is already uninitialized and cannot access to the affected endpoints.',
                            fg='magenta')
                continue

            if no_confirmation or status == AuthStateStatus.REAUTH_REQUIRED or click.confirm('Do you want to proceed?'):
                if status == AuthStateStatus.REAUTH_REQUIRED:
                    click.secho('The client is already required the re-authentication. Removing the session '
                                'automatically.',
                                fg='green')
                with echo_progress('Revoking the session...', 'DONE', 'green'):
                    authenticator.revoke()

                endpoint_ids_with_access_removed.extend(affected_endpoint_ids)
            else:
                continue

        echo_header('Summary')

        if endpoint_ids_with_access_removed:
            echo_list('The client is no longer authenticated to the follow endpoints:',
                      endpoint_ids_with_access_removed)
        else:
            click.echo('No changes')

        print()

    def get_states(self, endpoint_ids: List[str] = None) -> Iterator[Dict[str, Any]]:
        endpoints = self._get_filtered_endpoints(endpoint_ids)
        for authenticator in self.get_authenticators(endpoint_ids):
            auth_state = authenticator.get_state()
            state = auth_state.dict()

            # Simplify the auth/session info
            state['auth_info'] = self._remove_none_entry_from(auth_state.auth_info)
            # When type is omitted, the type is default to 'oauth2'.
            if not state['auth_info'].get('type'):
                state['auth_info']['type'] = 'oauth2'

            current_hash = ConfigurationModelMixin.hash(state['auth_info'])

            # Retrieve the associated endpoints.
            state['endpoints'] = []
            for endpoint in endpoints:
                for auth_info in endpoint.get_authentications():
                    # When type is omitted, the type is default to 'oauth2'.
                    if not auth_info.get('type'):
                        auth_info['type'] = 'oauth2'

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
        # NOTE: This is currently designed exclusively to work with OAuth2 config.
        #       Need to rework (on the output) to support other types of authenticators.

        authenticators = self.get_authenticators(endpoint_ids)
        with click.progressbar(authenticators, label='Authentication', show_eta=False, show_percent=True) as bar:
            for authenticator in bar:
                print()

                state = authenticator.get_state()

                url = state.auth_info.get('resource_url')
                client_id = state.auth_info.get('client_id')
                auth_scope = state.auth_info.get('scope')

                echo_header(f'Client ID: {client_id}\nResource URL: {url}',
                            bg='green' if state.status == AuthStateStatus.READY else 'blue')

                if state.status == AuthStateStatus.READY:
                    click.secho('>>> Already authenticated\n', dim=True)
                    continue

                if auth_scope:
                    parsed_scopes = sorted(auth_scope.split(r' '))
                    echo_list(
                        f'Requesting Specific Scope(s):',
                        parsed_scopes
                    )

                if revoke_existing:
                    with echo_progress(f'Revoking existing session... ', 'done', 'blue'):
                        authenticator.revoke()

                with echo_progress('Authenticating...', 'ok', 'green'):
                    authenticator.initialize()

                print()

    def get_authenticators(self, endpoint_ids: List[str] = None) -> List[Authenticator]:
        filtered_endpoints = self._get_filtered_endpoints(endpoint_ids)
        return HttpAuthenticatorFactory.create_multiple_from(endpoints=filtered_endpoints)

    def _get_filtered_endpoints(self, endpoint_ids: List[str] = None) -> List[ServiceEndpoint]:
        return [
            endpoint
            for endpoint in self._config_manager.load().endpoints
            if not endpoint_ids or endpoint.id in endpoint_ids
        ]
