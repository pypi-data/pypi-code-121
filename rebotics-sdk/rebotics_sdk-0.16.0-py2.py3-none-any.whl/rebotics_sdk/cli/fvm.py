import os
import pathlib

import click

from rebotics_sdk.cli.common import configure, shell, roles, set_token
from rebotics_sdk.cli.utils import read_saved_role, process_role, ReboticsCLIContext, app_dir, pass_rebotics_context
from rebotics_sdk.providers.fvm import FVMProvider
from .. import utils
from ..advanced import remote_loaders
from ..providers import ProviderHTTPClientException


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='fvm.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('fvm'), help="Key to specify what fvm to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Admin CLI tool to communicate with FVM API
    """
    process_role(ctx, role, 'fvm')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=FVMProvider
    )


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')


@api.command(name='file')
@click.option('-f', '--name', required=True, help='Filename of the file', type=click.UNPROCESSED)
@pass_rebotics_context
def virtual_upload(ctx, name):
    """Create virtual upload"""
    if ctx.verbose:
        click.echo('Calling create virtual upload')
    result = ctx.provider.create_virtual_upload(
        name
    )
    if 'id' in result.keys():
        pk = result['id']
        with open(name, 'rb', ) as fio:
            click.echo('Uploading file...')
            remote_loaders.upload(destination=result['destination'], file=fio, filename=name)
            ctx.provider.finish(
                pk
            )
            click.echo("Successfully finished uploading")
    else:
        click.echo("Failed to call virtual upload")


@api.group()
def rcdb():
    pass


def _download_rcdb_locally(ctx, rcdb_file, target):
    rcdb_file = str(rcdb_file)

    if rcdb_file.isdigit():
        # download rcdb file by ID
        try:
            response = ctx.provider.get_rcdb_by_id(int(rcdb_file))
        except ProviderHTTPClientException as exc:
            raise click.ClickException(f"Failed to trigger by API with error: {exc}")
        # should we also save a response? probably no
        return _download_rcdb_locally(ctx, response['file']['file'], target)  # get the url
    elif utils.is_url(rcdb_file):
        # download rcdb file by URL
        filename = utils.get_filename_from_url(rcdb_file)
        local_filepath = pathlib.Path(target / filename)
        try:
            remote_loaders.download(rcdb_file, local_filepath)
        except Exception as exc:
            raise click.ClickException(f"Failed to download file by URL: {exc}")
        return _download_rcdb_locally(ctx, local_filepath, target)
    else:
        # assuming that it is a local file path
        local_filepath = pathlib.Path(rcdb_file)
        if not local_filepath.exists():
            raise click.ClickException("Local file is not loaded!")
        return local_filepath


@rcdb.command(name="unpack")
@click.argument('rcdb_file')
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-w', '--with-images', is_flag=True)
@pass_rebotics_context
def rcdb_unpack(ctx, rcdb_file, target, with_images):
    rcdb_file = _download_rcdb_locally(ctx, rcdb_file, target)
    # create new packer and unpacker
