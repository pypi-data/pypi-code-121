import click
from imagination import container
from time import sleep

from dnastack.helpers.client_factory import ConfigurationBasedClientFactory
from ..utils import handle_error_gracefully
from ...client.base_client import BaseServiceClient
from ...exceptions import LoginException
from ...http.authenticators.abstract import Authenticator, FeatureNotAvailable


@click.group("auth", hidden=True)
def auth():
    pass


def _get_client(adapter_type: str) -> BaseServiceClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    client_class = factory.get_client_class(adapter_type)
    client = factory.get(client_class)

    if not client:
        raise LoginException(msg="There is no configured service")
    elif not client.require_authentication():
        raise LoginException(msg="The authentication information is not defined")
    return client


@auth.command("login")
@click.argument("service")
@click.option("--delay-init", type=int, required=False, default=0, help='Delay the authentication by seconds')
@click.option("--revoke-existing", is_flag=True, default=False, help='If used, the existing session will be automatically revoked before the re-authentication')
@handle_error_gracefully
def cli_login(service: str, delay_init: int, revoke_existing: bool):
    click.secho('You do not need to initiate the authentication process manually as it will be done automatically '
                'whenever needed, e.g., first request, session expired, etc.',
                fg='black',
                bg='yellow')

    if delay_init > 0:
        sleep(delay_init)

    service_client = _get_client(service)
    authorizer: Authenticator = service_client.get_current_authenticator()

    if revoke_existing:
        try:
            authorizer.revoke()
        except FeatureNotAvailable:
            pass

    authorizer.authenticate()

    click.secho("Login successful", fg="green")

