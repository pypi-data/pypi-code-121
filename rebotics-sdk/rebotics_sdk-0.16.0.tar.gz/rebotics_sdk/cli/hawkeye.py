import os

import click

from rebotics_sdk.cli.common import configure, shell, roles, set_token
from rebotics_sdk.cli.utils import read_saved_role, process_role, ReboticsCLIContext, app_dir, pass_rebotics_context
from rebotics_sdk.providers import ProviderHTTPServiceException
from rebotics_sdk.providers.hawkeye import HawkeyeProvider


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='hawkeye.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('hawkeye'), help="Key to specify what hawkeye to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Admin CLI tool to communicate with Hawkeye API
    """
    process_role(ctx, role, 'hawkeye')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=HawkeyeProvider
    )


@api.command(name='heartbeat')
@click.option('-c', '--camera', required=True, help='Shelf Camera ID to save its heartbeat data')
@click.option('-b', '--battery', required=True, help='Battery status of the camera', type=click.FLOAT)
@click.option('-f', '--free-storage', 'free_storage', required=True, help='Free storage of the Camera',
              type=click.FLOAT)
@click.option('-u', '--used-storage', 'used_storage', required=True, help='Used storage of the Camera',
              type=click.FLOAT)
@pass_rebotics_context
def create_camera_heartbeat(ctx, camera, battery, free_storage, used_storage):
    """Saves camera heartbeat data and returns the camera's list of actions"""
    try:
        if ctx.verbose:
            click.echo('Calling create camera heartbeat')
        result = ctx.provider.save_camera_heartbeat(
            camera,
            battery,
            free_storage,
            used_storage
        )
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='fixture')
@click.option('-i', '--store', required=True, help='Store ID of a fixture', type=click.STRING)
@click.option('-a', '--aisle', required=True, help='Aisle of a fixture', type=click.STRING)
@click.option('-s', '--section', required=True, help='Section of a fixture', type=click.STRING)
@click.option('-r', '--retailer', required=True, help='Retailer of a fixture', type=click.STRING)
@pass_rebotics_context
def create_fixture(ctx, store, aisle, section, retailer):
    """Saves Fixture object and returns ..."""
    try:
        if ctx.verbose:
            click.echo('Calling create fixture')
        result = ctx.provider.save_fixture(
            store,
            aisle,
            section,
            retailer
        )
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='fixtures')
@pass_rebotics_context
def get_list_fixtures(ctx):
    """Shows list of fixtures"""
    try:
        if ctx.verbose:
            click.echo('Calling get fixtures')
        result = ctx.provider.get_fixtures()
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='fixture-delete')
@click.option('-i', '--pk', required=True, help='ID of a fixture to be deleted', type=click.STRING)
@pass_rebotics_context
def delete_fixture(ctx, pk):
    """Shows list of fixtures"""
    try:
        if ctx.verbose:
            click.echo('Calling delete fixture')
        result = ctx.provider.delete_fixture(
            pk=pk
        )
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='retail')
@click.option('-c', '--codename', help='Codename of the retailer', type=click.STRING)
@click.option('-t', '--token', help='Token of the retailer', type=click.STRING)
@pass_rebotics_context
def create_retailer(ctx, codename, token):
    """Create Retailer object"""
    try:
        if ctx.verbose:
            click.echo('Calling create retailer')
        result = ctx.provider.save_retailer(
            codename,
            token
        )
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='camera')
@click.option('-c', '--camera', required=True, help='Camera ID of the Shelf Camera', type=click.STRING)
@click.option('-a', '--added', required=True, help='Who added the camera (ID)', type=click.INT)
@click.option('-f', '--fixture', required=True, help='Fixture ID of the camera', type=click.INT)
@pass_rebotics_context
def create_shelf_camera(ctx, camera, added, fixture):
    """Saves ShelfCamera object"""
    try:
        if ctx.verbose:
            click.echo('Calling create shelf camera')
        result = ctx.provider.create_shelf_camera(
            camera,
            added,
            fixture
        )
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='cameras')
@pass_rebotics_context
def get_list_shelf_cameras(ctx):
    """Shows list of shelf cameras"""
    try:
        if ctx.verbose:
            click.echo('Calling create shelf camera')
        result = ctx.provider.get_shelf_cameras()
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='capture')
@click.option('-c', '--camera', required=True, help='camera_id of the Capture object', type=click.STRING)
@click.option('-f', '--filekey', required=True, help='File key to be set in Capture object', type=click.STRING)
@click.option('-b', '--bucket-name', required=True, help='Bucket name to bet set in Capture object', type=click.STRING)
@pass_rebotics_context
def create_capture(ctx, camera, filekey, bucket_name):
    """Create Capture object with file_id to be configured, and ignored MEDIA_ROOT configuration"""
    click.echo('enters')
    try:
        if ctx.verbose:
            click.echo('Calling create capture')
        result = ctx.provider.save_capture(
            camera,
            filekey,
            bucket_name
        )
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
