import time
from typing import Optional

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from simple_rest_client.exceptions import ClientError

from vgscli.api import create_account_mgmt_api, create_vault_mgmt_api
from vgscli.cli.types import ResourceId, ResourceIdParamType
from vgscli.errors import handle_errors, ServiceClientCreationError, VgsCliError
from vgscli.serializers import dump_camelized_yaml
from vgscli.utils import validate_yaml


@with_plugins(iter_entry_points('vgs.apply.plugins'))
@click.group('apply')
def apply() -> None:
    """
    Create or update a VGS resource.
    """
    pass


@apply.command('service-account')
@click.option(
    '-O', '--organization', 'org_id',
    type=ResourceIdParamType(prefix='AC'),
    help='ID of the organization to associate the vault with.',
)
@click.option(
    '--file', '-f',
    type=click.File(),
    help='Configuration to apply.',
    required=True,
)
@click.pass_context
@handle_errors()
def apply_service_account(ctx: click.Context, org_id: ResourceId, file) -> None:
    """
    Create a Service Account client.
    """
    data = validate_yaml(file, 'validation-schemas/service-account-schema.yaml')['data']

    account_mgmt = create_account_mgmt_api(ctx)
    try:
        # noinspection PyUnresolvedReferences
        response = account_mgmt.service_accounts.create(org_id.base58, body={
            'data': {
                'attributes': {
                    'name': data['name'],
                    'annotations': data.pop('annotations', {}),
                    'scopes': data['scopes'],
                    'access_token_lifespan': data.get('accessTokenLifespan', None)
                }
            }
        })
    except ClientError as cause:
        raise ServiceClientCreationError(cause)

    attributes = response.body['data']['attributes']

    data['clientId'] = attributes['client_id']
    data['clientSecret'] = attributes['client_secret']

    # NOTE: Annotations are excluded from the output as they are undesirably camelized
    # (e.g., "vgs.io/vault-id" becomes "vgs.io/vaultId")

    click.echo(dump_camelized_yaml({
        'apiVersion': '1.0.0',
        'kind': 'ServiceAccount',
        'data': data,
    }))


@apply.command('vault')
@click.option(
    '-O', '--organization', 'org_id',
    type=ResourceIdParamType(prefix='AC'),
    help='ID of the organization to associate the vault with.',
)
@click.option(
    '--file', '-f',
    type=click.File(),
    help='Configuration to apply.',
    required=True,
)
@click.pass_context
@handle_errors()
def apply_vault(ctx: click.Context, org_id: Optional[ResourceId], file) -> None:
    """
    Create a new VGS vault.
    """
    data = validate_yaml(file, 'validation-schemas/vault-schema.yaml')['data']

    # kubectl behavior
    if 'organizationId' in data:
        if org_id and org_id.base58 != data['organizationId']:
            raise VgsCliError(
                f"Ambiguous organization ID. "
                f"Run the command with '--organization={data['organizationId']}' to resolve."
            )
    else:
        if not org_id:
            raise VgsCliError("Missing organization ID. Pass the '--organization' option to resolve.")

        data['organizationId'] = org_id.base58

    account_mgmt = create_account_mgmt_api(ctx)

    # noinspection PyUnresolvedReferences
    response = account_mgmt.vaults.create_or_update(body={
        'data': {
            'attributes': {
                'name': data['name'],
                'environment': data['environment']
            },
            'type': 'vaults',
            'relationships': {
                'organization': {
                    'data': {
                        'type': 'organizations',
                        'id': data['organizationId']
                    }
                }
            }
        }
    })

    attributes = response.body['data']['attributes']

    data['id'] = attributes['identifier']
    data['credentials'] = {
        'username': attributes['credentials']['key'],
        'password': attributes['credentials']['secret'],
    }

    vault_mgmt = create_vault_mgmt_api(ctx, response.body['data']['links']['vault_management_api'])

    while True:
        # noinspection PyUnresolvedReferences
        response = vault_mgmt.vaults.retrieve(data['id'], headers={'VGS-Tenant': data['id']})
        if response.body['data']['attributes']['state'] == 'PROVISIONED':
            break
        time.sleep(2)

    click.echo(dump_camelized_yaml({
        'apiVersion': '1.0.0',
        'kind': 'Vault',
        'data': data,
    }))
