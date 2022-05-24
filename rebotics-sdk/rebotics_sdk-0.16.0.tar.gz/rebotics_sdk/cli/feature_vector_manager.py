import logging
import os

import click

from .common import shell, roles, configure, set_token
from .utils import ReboticsCLIContext, pass_rebotics_context, app_dir, process_role, read_saved_role
from ..providers import RetailerProvider

logger = logging.getLogger(__name__)


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='fvm.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('retailer'), help="Key to specify what retailer to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Retailer CLI tool to communicate with retailer API
    """
    process_role(ctx, role, 'fvm')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=RetailerProvider
    )


@api.command()
@pass_rebotics_context
def version(ctx):
    """Show retailer backend version"""
    ctx.format_result(ctx.provider.version(), 100)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.argument('files', nargs=-1, required=True, type=click.File('rb'))
@pass_rebotics_context
def upload_files(ctx, input_type, store, files):
    """
    Upload processing files to the retailer backend, that can be used as processing action inputs
    """
    file_ids = []
    for f_ in files:
        response = ctx.provider.processing_upload(
            store, f_, input_type
        )
        file_ids.append(response['id'])

        if ctx.verbose:
            click.echo(response)  # redirecting this output to stderr
    click.echo(' '.join(map(str, file_ids)))


@api.group(name='fv')
def feature_vectors():
    """
    Feature vector flow
    """
    pass


@feature_vectors.command('list')
@pass_rebotics_context
def feature_vectors_list(ctx):
    fve = ctx.provider.feature_vectors_export()
    data = fve.get()
    if data:
        ctx.format_result(data)


@feature_vectors.command('export')
@click.option('-b', '--batch-size', type=click.INT, default=50000)
@click.option('-s', '--source-model', default='')
@click.option('-r', '--result-model', default='previews-backup')
@pass_rebotics_context
def feature_vectors_export(ctx, source_model, result_model, batch_size):
    fve = ctx.provider.feature_vectors_export()
    result = fve.export(source_model=source_model, result_model=result_model, batch_size=batch_size)
    ctx.format_result(result)


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
