import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from simple_rest_client.exceptions import ClientError, ServerError

from vgscli.api import create_account_mgmt_api
from vgscli.cli.types import ResourceId, ResourceIdParamType
from vgscli.errors import handle_errors, ServiceClientListingError
from vgscli.serializers import dump_camelized_yaml


@with_plugins(iter_entry_points('vgs.get.plugins'))
@click.group('get')
def get() -> None:
    """
    Get VGS resource.
    """
    pass


@get.command('service-accounts')
@click.option(
    '-O', '--organization', 'org_id',
    type=ResourceIdParamType(prefix='AC'),
    help='Organization ID which service accounts will be listed',
)
@click.pass_context
@handle_errors()
def get_service_accounts(ctx: click.Context, org_id: ResourceId):
    """
    Get service accounts from the organization.
    """

    account_mgmt = create_account_mgmt_api(ctx)
    try:
        # noinspection PyUnresolvedReferences
        response = account_mgmt.service_accounts.get(org_id.base58)
    except (ClientError, ServerError) as e:
        raise ServiceClientListingError(e)

    accounts = response.body['data']['attributes']['service_accounts']

    for account in accounts:
        click.echo('---')
        click.echo(dump_camelized_yaml({
            'apiVersion': '1.0.0',
            'kind': 'ServiceAccount',
            'data': account,
        }))