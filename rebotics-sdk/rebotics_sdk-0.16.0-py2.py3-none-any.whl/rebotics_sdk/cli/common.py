import hashlib
import os
import pathlib
import shlex
import subprocess as s
import uuid
from datetime import datetime
from pprint import pformat

import chardet
import click
import six
import yaml

from rebotics_sdk.cli.renderers import format_full_table
from rebotics_sdk.cli.utils import pass_rebotics_context
from rebotics_sdk.providers import ProviderHTTPClientException


def mean(arr):
    return sum(arr) / len(arr)


@click.group()
@click.version_option()
def main():
    """Collection of scripts for rebotics"""
    pass


@main.command()
@click.argument('container')
@click.argument('volume')
def fix_pycharm(container, volume):
    with s.Popen(shlex.split("docker ps -a --format '{{.Names}}'"), stdout=s.PIPE) as proc:
        containers = proc.stdout.read().decode('utf-8').split('\n')
        assert container in containers, 'Container should exist'

    # save helpers to the tmp folder
    tmp_folder = '/tmp/helper_folder_%s' % uuid.uuid4()
    os.system('docker cp {container}:/opt/.pycharm_helpers {tmp_folder}'.format(
        container=container,
        tmp_folder=tmp_folder
    ))

    # assign new container with attached volume
    helper_random_name = 'helper_%s' % uuid.uuid4()
    os.system('docker run -v {target_volume}:/opt/.pycharm_helpers --name {name} busybox true'.format(
        target_volume=volume,
        name=helper_random_name,
    ))

    os.system('docker cp {tmp_folder} {name}:/opt/.pycharm_helpers'.format(
        tmp_folder=tmp_folder,
        name=helper_random_name
    ))

    # Cleanup
    os.system('docker rm -f {helper_random_name}'.format(helper_random_name=helper_random_name))
    os.system('rm -rf {tmp_folder}'.format(tmp_folder=tmp_folder))
    click.echo('Finished')


@main.command()
@click.option("-p", "--pycharm_folder", help="pycharm folder from where to start", type=click.Path())
def fix_pycharm_clean(pycharm_folder):
    """
    This command fixes all pycharm related volumes and merges the helpers folder to it.
    This is in case when you update pycharm and run with debugger, but it yields error:
    python: can't open file '/opt/.pycharm_helpers/pydev/pydevd.py': [Errno 2] No such file or directory
    python: can't open file '/opt/.pycharm_helpers/generator3/__main__.py': [Errno 2] No such file or directory
    """

    def find_pycharm_helpers_folders(base_folder):
        for dirpath, dirnames, filenames in os.walk(os.path.expanduser(base_folder)):
            if 'PyCharm' in dirpath:
                if '/helpers' in dirpath and '/helpers/' not in dirpath:  # get only the top folder
                    if 'pydev' in dirnames:
                        yield dirpath

    helper_folder = ''
    if pycharm_folder is not None:
        base_folder = pathlib.Path(pycharm_folder)
    else:
        base_folder = "~"

    for path in find_pycharm_helpers_folders(base_folder):
        helper_folder = path
        break
    click.echo('Using helper folder: {helper_folder}'.format(
        helper_folder=helper_folder
    ))

    with s.Popen(shlex.split("docker volume ls --format '{{ .Name }}'"), stdout=s.PIPE) as proc:
        volumes = proc.stdout.read().decode('utf-8').split('\n')

    for volume in volumes:
        if 'helpers' not in volume:
            continue
        click.echo('Fixing pycharm_helpers for {volume}'.format(volume=volume))
        # assign new container with attached volume
        container = 'helper_%s' % uuid.uuid4()
        os.system('docker run -v {volume}:/opt/.pycharm_helpers --name {container} busybox true'.format(
            volume=volume,
            container=container
        ))
        os.system('docker cp {helper_folder}/. {container}:/opt/.pycharm_helpers/'.format(
            helper_folder=helper_folder,
            container=container
        ))

        # Cleanup
        os.system('docker rm -f {container}'.format(container=container))
    click.echo('Finished')


@main.command()
def install_bash_completion():
    path = os.path.expanduser('~/.bashrc')

    with open(path, 'a') as bashrc:
        commands = [
            '# Rebotics scripts autocomplete scripts',
            '# After you uninstall rebotics-scripts, please consider to delete this too',
            'eval "$(_RETAILER_COMPLETE=source retailer)"',
            'eval "$(_ADMIN_COMPLETE=source admin)"',
            'eval "$(_DATASET_COMPLETE=source dataset)"',
            'eval "$(_REBOTICS_COMPLETE=source rebotics)"',
            'eval "$(_CAMERA_MANAGER_COMPLETE=source camera_manager)"',
        ]
        for command in commands:
            bashrc.write(command + "\n")

    click.edit(filename=path)


@main.command()
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
@click.option('-e', '--encoding')
@click.option('-t', '--target', type=click.Path(exists=False))
def encode_utf8(filepath, encoding, target):
    if not encoding:
        with open(filepath, 'rb') as f_:
            possible_encoding_detected = chardet.detect(f_.read())
            encoding = possible_encoding_detected['encoding']
    try:
        import pandas as pd
    except ImportError:
        raise click.ClickException('You need to have pandas installed to use this feature')

    try:
        df = pd.read_csv(filepath, encoding=encoding, dtype=object)
    except Exception as exc:
        raise click.ClickException('Can not read the file. Error: %s' % exc)

    if not target:
        full_name, extension = filepath.rsplit('.', 1)
        target = '{}_utf8.{}'.format(full_name, extension)

    try:
        df.to_csv(target, encoding='utf-8')
    except Exception as exc:
        raise click.ClickException('Failed to save the csv file, %s' % exc)
    click.echo('File saved at {}'.format(target))


@click.command()
@pass_rebotics_context
def shell(ctx):
    """Opens interactive IPython shell """
    click.echo('you can use current ctx, requests, provider')
    user_ns = {
        'provider': ctx.provider,
        'ctx': ctx,
        'requests': ctx.provider.requests,
    }

    try:
        import pandas as pd
        click.echo('import pandas as pd')
        user_ns['pd'] = pd
    except ImportError:
        pass

    try:
        from IPython import start_ipython
        start_ipython(
            argv=[],
            user_ns=user_ns
        )
    except ImportError:
        click.echo('You need to install rebotics_sdk[shell] and you also required to use Python3.5+')


@click.command()
@click.option('-l', '--locate', is_flag=True, default=False)
@pass_rebotics_context
def roles(ctx, locate):
    """List available roles to use"""
    if locate:
        click.echo(ctx.config_path)
        return
    config = ctx.config
    if ctx.format == 'json':
        click.echo(pformat(config.config, indent=2))
    elif ctx.format == 'id':
        for key, value in config.config.items():
            click.echo(key)
    elif ctx.format == 'table':
        role_configurations = []
        for key, value in config.items():
            data = value
            data['role'] = key
            role_configurations.append(data)
        click.echo(format_full_table(role_configurations, 100))


def option_default_from_configurations(conf_name):
    class _Option(click.Option):
        def get_default(self, ctx):
            # try to fetch configuration from conf_name
            if ctx.parent is None:
                raise click.ClickException('This command is supposed to be used as sub command.')
            role = ctx.parent.params.get('role')
            role_config = ctx.obj.config.get(role)
            if role_config is not None:
                self.default = role_config.get(conf_name)
            return super(_Option, self).get_default(ctx)

    return _Option


@click.command()
@click.option('-h', '--host', help='App host', prompt=True, cls=option_default_from_configurations('host'))
@click.option('-u', '--user', prompt=True, cls=option_default_from_configurations('username'))
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@pass_rebotics_context
def configure(ctx, user, password, host):
    """Fetch token, save it and use the role of it."""
    provider = ctx.provider_class(host=host)
    ctx.update_configuration(
        host=host,
    )
    try:
        response = provider.token_auth(user, password)
    except ProviderHTTPClientException as e:
        raw_message = e.response.content.decode('utf-8')
        if '2FA' in raw_message or 'code' in raw_message:
            click.echo('Please enter the verification code from email.')
            token = input('Verification code from email: ')
            response = provider.token_auth(user, password, verification_code=token)
        else:
            click.echo("Failed to login because of %s" % str(e))
            return

    ctx.update_configuration(
        host=host,
        date=datetime.now().strftime('%c'),
        **response.json()
    )
    click.echo('Saved configuration for {} in {}'.format(ctx.role, ctx.config_provider.filepath), err=True)
    ctx.format_result(response.json())


@click.command()
@click.option('-h', '--host', help='App host', prompt=True, cls=option_default_from_configurations('host'))
@click.option('--token', prompt=True, hide_input=True, confirmation_prompt=False)
@pass_rebotics_context
def set_token(ctx, host, token):
    """
    Set raw authorization token
    """
    ctx.update_configuration(
        host=host,
        date=datetime.now().strftime('%c'),
        token=token,
    )
    click.echo('Saved configuration for {} in {}'.format(ctx.role, ctx.config_provider.filepath), err=True)


@click.command()
@click.argument('source_file', type=click.File('r'))
@pass_rebotics_context
def run(ctx, source_file):
    click.echo(six.exec_(source_file.read(), {
        'ctx': ctx,
        'provider': ctx.provider,
    }))


@main.command()
@click.argument('codeword')
@click.argument('param')
def signature(codeword, param):
    click.echo(hashlib.md5(str(codeword + param).encode('utf-8')).hexdigest())


@main.command()
@click.argument('compose_file', type=click.Path(exists=True, dir_okay=False))
def clear_ports(compose_file):
    try:
        import psutil
    except ImportError:
        raise ImportError('Try to install psutil')

    compose_absolute_path = pathlib.Path(compose_file).absolute()
    with s.Popen("docker-compose -f {} config".format(compose_absolute_path), stdout=s.PIPE) as proc:
        config = proc.stdout.read().decode('utf-8')
    conf = yaml.load(config, Loader=yaml.SafeLoader)

    for service_name, value in conf['services'].items():
        for ports_map in value.get('ports', []):
            try:
                published = ports_map['published']
            except Exception:
                continue

            connections = [p for p in psutil.net_connections() if p.laddr.port == published]

            for con in connections:
                click.echo("{}:{} {}".format(service_name, ports_map, con))
                try:
                    proc = psutil.Process(con.pid)
                    proc.kill()
                except Exception:
                    pass
