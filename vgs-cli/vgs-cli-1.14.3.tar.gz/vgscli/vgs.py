import os
from typing import Optional

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from jinja2 import Environment, PackageLoader, StrictUndefined, UndefinedError

from vgscli import auth
from vgscli._version import check_for_updates, version
from vgscli.access_logs import prepare_filter, fetch_logs
from vgscli.accounts_api import create_api as create_accounts_api, \
    delete_service_account as remove_service_account
from vgscli.audits_api import create_api as create_audits_api, OperationLogsQueryConfig
from vgscli.auth import client_credentials_login, handshake, token_util
from vgscli.click_extensions import Config, DateTimeDuration
from vgscli.config_file import configuration_option
from vgscli.errors import handle_errors
from vgscli.routes import dump_all_routes, sync_all_routes
from vgscli.serializers import wrap_records, format_logs
from vgscli.utils import resolve_env
from vgscli.vaults_api import create_api as create_vaults_api
from vgscli.cli.commands import apply, generate, get
from vgscli.cli.types import VariableParamType


@with_plugins(iter_entry_points('vgs.plugins'))
@click.group()
@click.option("--debug", "-d", is_flag=True, help="Enables debug mode.", default=False)
@click.option("--environment", "-e", help="VGS environment.", hidden=True)
@click.version_option(message='%(version)s', version=version())
@click.pass_context
def cli(ctx, debug, environment):
    """
    Command Line Tool for programmatic configurations on VGS.
    """
    ctx.debug = debug

    env = resolve_env(environment)
    ctx.obj = Config(debug, env)

    client_id = os.environ.get('VGS_CLIENT_ID')
    client_secret = os.environ.get('VGS_CLIENT_SECRET')

    if client_id and client_secret:
        client_credentials_login(ctx, client_id, client_secret, env)


cli.add_command(get)
cli.add_command(apply)
cli.add_command(generate)


@with_plugins(iter_entry_points('vgs.delete.plugins'))
@cli.group()
def delete():
    """
    Delete VGS resource.
    """
    pass


@with_plugins(iter_entry_points('vgs.logs.plugins'))
@cli.group()
def logs():
    """
    Prints VGS logs.

    \b\bExamples:

    # Show all access logs for a vault\t\t\t\t\t\t
    vgs logs access -V <VAULT_ID>

    # Show all operation logs for request\t\t\t\t\t\t
    vgs logs operations -V <VAULT_ID> -R <REQUEST_ID>
    """
    pass


def validate_tail(ctx, param, value):
    try:
        if value > 0:
            return value
        elif value != -1:
            raise ValueError
    except ValueError:
        raise click.BadParameter('need to be positive value, larger than 0')


@logs.command('access', short_help='Get access logs')
@click.option('--output', '-o', help='Output format', type=click.Choice(['json', 'yaml']), default='yaml',
              show_default=True)
# @click.option('--follow', '-f', help='Specify to stream logs as they appear on the VGS dashboard.', is_flag=True, default=False)
@click.option('--since',
              help='Only show logs newer than a relative duration like 30s, 5m, or 3h or after a specific RFC 3339 date.',
              type=DateTimeDuration(formats=["%Y-%m-%dT%H:%M:%S"]))
@click.option('--tail', help='Number of log records to show. Defaults to all logs if unspecified.', default=-1,
              callback=validate_tail)
@click.option('--until',
              help='Only show logs older than a relative duration like 30s, 5m, or 3h or before a specific RFC 3339 date.',
              type=DateTimeDuration(formats=["%Y-%m-%dT%H:%M:%S"]))
@click.option('--vault', '-V', help="Vault ID", required=True)
@click.option('--proxy', '-P', help="Show access logs for a specific proxy",
              type=click.Choice(['http', 'sftp', 'iso8583']))
@click.pass_context
def access(ctx, vault, proxy, **kwargs):
    """
    Get access logs

    \b\bExamples:

    # Show access logs available for a vault\t\t\t\t\t\t
    vgs logs access -V <VAULT_ID>

    # Show access logs in the last hour\t\t\t\t\t\t
    vgs logs access -V <VAULT_ID> --since=1h

    # Show access logs after a specific date\t\t\t\t\t\t
    vgs logs access -V <VAULT_ID> --since=2020-08-18T11:40:45

    # Show only the most recent 25 log records\t\t\t\t\t\t
    vgs logs access -V <VAULT_ID> --tail=25
    """
    handshake(ctx, ctx.obj.env)

    audits_api = create_audits_api(ctx, vault, ctx.obj.env, token_util.get_access_token())

    filters = prepare_filter({
        'tenant_id': vault,
        'protocol': proxy,
        'from': kwargs.get('since'),
        'to': kwargs.get('until'),
    })

    for res in fetch_logs(audits_api, filters, kwargs.get('tail')):
        click.echo(format_logs(wrap_records(res), kwargs.get('output')))

    # while kwargs['follow']:
    #     res = fetch_logs(audits_api, filters, kwargs.get('tail'))
    #     click.echo(format_logs(res, kwargs.get('output')))
    #     time.sleep(3)


@logs.command('operations', short_help='Get operations logs')
@click.option('--output', '-o', help='Output format', type=click.Choice(['json', 'yaml']), default='yaml',
              show_default=True)
@click.option('--vault', '-V', help="Vault ID", required=True)
@click.option('--request', '-R', help="VGS Request ID", required=True)
@click.pass_context
def operations_logs(ctx, vault, request, **kwargs):
    """
    Get operations logs

    \b\bExamples:

    # Return operation logs for a request\t\t\t\t\t\t
    vgs logs operations -V <VAULT_ID> -R <REQUEST_ID>

    # Return operations logs for a request in JSON format\t\t\t\t\t\t
    vgs logs operations -V <VAULT_ID> -R <REQUEST_ID> -o json
    """
    handshake(ctx, ctx.obj.env)

    audits_api = create_audits_api(ctx, vault, ctx.obj.env, token_util.get_access_token())
    config = OperationLogsQueryConfig(vault, trace_id=request)

    logs = fetch_operations_logs(audits_api, config.to_query_params())
    click.echo(format_logs(wrap_records(logs), kwargs.get('output')))


def fetch_operations_logs(api, params):
    return api.operations_logs.list(params=params).body['data']


@get.command('routes')
@click.option("--vault", "-V", help="Vault ID", required=True)
@click.pass_context
@handle_errors()
def get_routes(ctx, vault):
    """
    Get routes
    """
    handshake(ctx, ctx.obj.env)

    routes_api = create_vaults_api(ctx, vault, ctx.obj.env, token_util.get_access_token())
    dump = dump_all_routes(routes_api)
    click.echo(dump)


# TODO: Move to cli.commands.apply
@apply.command('routes')
@click.option("--vault", "-V", help="Vault ID", required=True)
@click.option("--filename", "-f", help="Filename for the input data", type=click.File('r'), required=True)
@click.pass_context
@handle_errors()
def apply_routes(ctx, vault, filename):
    """
    Create or update VGS routes.
    """
    handshake(ctx, ctx.obj.env)

    route_data = filename.read()
    vault_management_api = create_vaults_api(ctx, vault, ctx.obj.env, token_util.get_access_token())
    sync_all_routes(vault_management_api, route_data,
                    lambda route_id: click.echo(f'Route {route_id} processed'))
    click.echo(f'Routes updated successfully for vault {vault}')


@delete.command('service-account')
@click.option("--organization", "-O", help="Organization ID", required=True)
@click.argument('client_id', type=click.STRING)
@click.pass_context
@handle_errors()
def delete_service_account(ctx, organization, client_id):
    """
    Delete service account client from the organization.
    """

    handshake(ctx, ctx.obj.env)

    accounts_api = create_accounts_api(token_util.get_access_token(), ctx.obj.env)
    remove_service_account(accounts_api, organization, client_id)


# TODO: Move to cli.commands.generate
@generate.command('service-account')
@click.option("--template", "-t", type=click.Choice(['vgs-cli', 'calm',
                                                     'checkout',
                                                     'sub-account-checkout',
                                                     'payments-admin']),
              help="Predefined service account template configuration", required=True)
@click.option('--var', 'variables', type=VariableParamType(), multiple=True, help='Template variables.')
@click.pass_context
@handle_errors()
def generate_service_account(ctx, template, variables):
    """
    Output a Service Account template.
    """
    environment = Environment(
        loader=PackageLoader(package_name="vgscli", package_path='resource-templates/service-account'),
        undefined=StrictUndefined
    )
    try:
        template = environment.get_template(f'{template}.yaml')
        click.echo(template.render(**{var.name: var.value for var in variables}))
    except UndefinedError as error:
        click.echo(click.style("Error!", fg="red") + f" Could not render service "
                                                     f"account template: {error}. "
                                                     f"Please use '--var variable=value' to pass required variable.")
        ctx.exit(1)


@cli.command()
@click.option(
    '--browser/--no-browser', 'open_browser',
    default=True,
    help='Open the default browser automatically.',
    show_default=True,
)
@click.option('--idp', help='Log in with a custom Identity Provider.')
@click.pass_context
@configuration_option(section='login')
def login(ctx, idp: Optional[str], open_browser: bool):
    """
    Login to VGS via browser.
    """
    check_for_updates()

    auth.login(ctx, ctx.obj.env, idp=idp, open_browser=open_browser)


@cli.command()
@click.pass_context
def logout(ctx):
    """
    Logout from VGS.
    """
    auth.logout(ctx, ctx.obj.env)


if __name__ == "__main__":
    cli()
