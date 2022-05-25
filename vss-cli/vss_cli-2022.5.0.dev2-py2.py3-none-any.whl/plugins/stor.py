"""VSS Storage Management plugin for VSS CLI (vss-cli)."""
from datetime import timedelta
import logging
import os

import click

from vss_cli import const
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.utils.emoji import EMOJI_UNICODE
from vss_cli.validators import validate_json_type

_LOGGING = logging.getLogger(__name__)


@click.group('stor', short_help='Manage your VSS storage account.')
@pass_context
def cli(ctx: Configuration):
    """Manage your VSS storage account."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command('la', short_help='launch ui')
@click.argument(
    'ui_type', type=click.Choice(['gui', 'admin', 's3api']), required=True
)
@click.option(
    '--show-cred/--no-show-cred', help='Show credentials or not', is_flag=True,
)
@pass_context
def stor_launch(ctx: Configuration, ui_type, show_cred):
    """Launch web ui."""
    ctx.get_vskey_stor()
    opts = {
        'gui': ctx.vskey_stor_s3_gui,
        's3api': ctx.vskey_stor_s3api,
        'admin': ctx.s3_server,
    }
    url = opts[ui_type]
    click.echo(f'Launching {EMOJI_UNICODE[":globe_showing_Americas:"]}: {url}')
    if ui_type in ['gui', 's3api']:
        if show_cred:
            click.echo(
                f'username: {ctx.vskey_stor_s3_ak}\n'
                f'password: {ctx.vskey_stor_s3_sk}\n'
            )
    click.launch(url,)


@cli.command('ls', short_help='list remote dir contents')
@click.option(
    '--bucket', type=click.STRING, help='Bucket to list.', default='ut-vss'
)
@click.argument('remote_path', type=click.STRING, default="/")
@pass_context
def stor_ls(ctx: Configuration, bucket, remote_path):
    """List contents of your VSKEY-STOR Space."""
    columns = ctx.columns or const.COLUMNS_STOR
    ctx.get_vskey_stor()
    with ctx.spinner(disable=ctx.debug):
        obj_gen = ctx.vskey_stor.list_objects(
            bucket, remote_path, recursive=True
        )
        obj = [o.object_name for o in obj_gen]
    click.echo(format_output(ctx, obj, columns=columns))


@cli.command('sh', short_help='share with pre-signed link')
@click.option(
    '--bucket',
    type=click.STRING,
    help='Bucket where file is stored.',
    default='ut-vss',
)
@click.option(
    '--expires', type=click.INT, help='Expiry time in hours.', default=2
)
@click.option('--launch', is_flag=True, help='Launch with default handler.')
@click.argument('remote_path', type=click.STRING, required=True)
@pass_context
def stor_share(ctx, remote_path, bucket, expires, launch):
    """Get a pre-signed link to download object."""
    ctx.get_vskey_stor()
    url = ctx.vskey_stor.get_presigned_url(
        "GET",
        bucket_name=bucket,
        object_name=remote_path,
        expires=timedelta(hours=expires),
    )
    obj = {'url': url}
    columns = ctx.columns or const.COLUMNS_STOR_SHARE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    if launch:
        click.echo(
            f'Launching {EMOJI_UNICODE[":globe_showing_Americas:"]}: {url}'
        )
        click.launch(url)


@cli.command('get', short_help='get info')
@click.option(
    '--bucket', type=click.STRING, help='Bucket to list.', default='ut-vss'
)
@click.argument('remote_path', type=click.STRING, required=True)
@pass_context
def stor_get(ctx, remote_path, bucket):
    """Get file info."""
    ctx.get_vskey_stor()
    columns = ctx.columns or const.COLUMNS_STOR_INFO
    obj_gen = ctx.vskey_stor.list_objects(
        bucket_name=bucket, prefix=remote_path
    )
    objs = [
        {
            'name': o.object_name,
            'bucket_name': o.bucket_name,
            'last_modified': o.last_modified,
            'size': o.size,
        }
        for o in obj_gen
    ]
    click.echo(format_output(ctx, objs, columns=columns, single=True))


@cli.command('dl', short_help='download file')
@click.argument('remote_path', type=click.STRING, required=True)
@click.option(
    '--bucket', type=click.STRING, help='Bucket to list.', default='ut-vss'
)
@click.option(
    '-d',
    '--dir',
    type=click.STRING,
    help='Local target directory',
    default=os.getcwd(),
)
@click.option('-n', '--name', type=click.STRING, help='Local target name')
@pass_context
def stor_dl(ctx: Configuration, remote_path, dir, name, bucket):
    """Download remote file."""
    ctx.get_vskey_stor()
    local_dir = os.path.expanduser(dir) or os.getcwd()
    local_name = name or os.path.basename(remote_path)
    local_path = os.path.join(local_dir, local_name)
    # check if remote path exists
    ctx.log(
        f'Download {remote_path} to {local_path} in '
        f'progress {EMOJI_UNICODE.get(":fast_down_button:")} '
    )
    with ctx.spinner(disable=ctx.debug):
        ctx.vskey_stor.fget_object(
            bucket_name=bucket, object_name=remote_path, file_path=local_path
        )
    ctx.log(
        f'Download complete to {local_path} '
        f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}'
    )


@cli.command('ul', short_help='upload file')
@click.argument('file_path', type=click.Path(exists=True), required=True)
@click.option(
    '--bucket', type=click.STRING, help='Bucket to list.', default='ut-vss'
)
@click.option(
    '-d',
    '--dir',
    type=click.STRING,
    help='Remote target directory',
    default='/',
)
@click.option(
    '-n',
    '--name',
    type=click.STRING,
    help='Remote target name',
    required=False,
)
@click.option(
    '-m',
    '--metadata',
    help='Key-Value JSON metadata.',
    callback=validate_json_type,
    type=click.STRING,
    required=False,
)
@pass_context
def stor_ul(ctx: Configuration, file_path, name, dir, bucket, metadata):
    """Upload file to your VSKEY-STOR space.

    This command is useful when a required ISO is
    not available in the VSS central repository and needs to be
    mounted to a virtual machine.
    """
    ctx.get_vskey_stor()
    file_name = name or os.path.basename(file_path)
    remote_base = dir
    # upload
    remote_path = os.path.join(remote_base, file_name)
    ctx.log(
        f'Upload {file_path} to {remote_path} '
        f'in progress {EMOJI_UNICODE.get(":fast_up_button:")}'
    )
    with ctx.spinner(disable=ctx.debug):
        kwargs = dict(
            bucket_name=bucket, object_name=name, file_path=file_path
        )
        if metadata is not None:
            kwargs['metadata'] = metadata
        result = ctx.vskey_stor.fput_object(**kwargs)
    ctx.echo(
        f'Upload complete to {result.object_name}, etag={result.etag}, '
        f'version-id={result.version_id} '
        f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}'
    )
