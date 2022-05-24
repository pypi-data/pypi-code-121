import json
import os
from multiprocessing import Pool

import click
import six

from rebotics_sdk.cli.renderers import format_processing_action_output, format_full_table
from rebotics_sdk.utils import download_file
from ..providers import RetailerProvider
from ..utils import mkdir_p

if six.PY2:
    FileNotFoundError = IOError

app_dir = click.get_app_dir('rebotics-scripts')
mkdir_p(app_dir)


class DumpableConfiguration(object):
    def __init__(self, path):
        self.path = path

    @property
    def filepath(self):
        return os.path.expanduser(self.path)

    @property
    def config(self):
        try:
            with open(self.filepath, 'r') as config_buffer:
                return json.load(config_buffer)
        except FileNotFoundError:
            self.config = {}
            return {}
        except (json.JSONDecodeError,):
            return {}

    @config.setter
    def config(self, value):
        with open(self.filepath, 'w') as config_buffer:
            json.dump(value, config_buffer, indent=2)

    def update_configuration(self, key, **configuration):
        current_configuration = self.config
        if key not in current_configuration:
            current_configuration[key] = configuration
        else:
            current_configuration[key].update(configuration)
        self.config = current_configuration


class ReboticsScriptsConfiguration(DumpableConfiguration):
    def __init__(self, path, provider_class=RetailerProvider):
        super(ReboticsScriptsConfiguration, self).__init__(path)
        self.provider_class = provider_class

    def get_provider(self, key):
        config = self.config.get(key, None)
        if config is None:
            return None

        provider_kwargs = {
            'host': config['host'],
            'role': key,
        }
        if 'token' in config:
            provider_kwargs['token'] = config['token']

        provider = self.provider_class(**provider_kwargs)
        return provider


class ReboticsCLIContext(object):
    configuration_class = ReboticsScriptsConfiguration

    def __init__(self, role, format, verbose, config_path, provider_class):
        self.role = role
        self.format = format
        self.verbose = verbose
        self.config_path = config_path
        self.provider_class = provider_class
        self.config_provider = self.configuration_class(self.config_path, self.provider_class)
        self.config = self.config_provider.config

    @property
    def provider(self):
        provider = self.config_provider.get_provider(self.role)

        if provider is None:
            raise click.ClickException('Role {0} is not configured.\n'
                                       'Run: \n<command> -r {0} configure'.format(self.role))
        return provider

    def update_configuration(self, **configuration):
        self.config_provider.update_configuration(self.role, **configuration)

    def format_result(self, items, max_column_length=30, keys_to_skip=None, force_format=None):
        force_format = force_format if force_format else self.format
        if force_format == 'json':
            click.echo(json.dumps(items, indent=2))
        elif force_format == 'id':
            click.echo(" ".join([str(item.get('id')) for item in items]))
        else:
            format_full_table(items, max_column_length=max_column_length, keys_to_skip=keys_to_skip)

    def verbose_log(self, message):
        if self.verbose:
            click.echo(message)


pass_rebotics_context = click.make_pass_decorator(ReboticsCLIContext, True)


class GroupWithOptionalArgument(click.Group):
    def parse_args(self, ctx, args):
        if args:
            if args[0] in self.commands:
                if len(args) == 1 or args[1] not in self.commands:
                    args.insert(0, '')
        super(GroupWithOptionalArgument, self).parse_args(ctx, args)


states = DumpableConfiguration(os.path.join(app_dir, 'command_state.json'))


def read_saved_role(command_name):
    roles = states.config.get('roles')
    if roles is None:
        return None
    role = roles.get(command_name)
    if role is not None:
        click.echo('Using previous role: {}'.format(role), err=True)
    return role


def process_role(ctx, role, command_name):
    if not role:
        if ctx.invoked_subcommand != 'roles':
            raise click.ClickException(
                'You have not specified role to use. User `roles` sub command to see what roles are available'
            )
    else:
        states.update_configuration('roles', **{command_name: role})


def task_runner(ctx, task_func, ids, concurrency, **kwargs):
    task_arguments = []

    for id_ in ids:
        arguments = {
            'ctx': ctx,
            'id': id_,
        }
        arguments.update(kwargs)
        task_arguments.append(arguments)

    pool = Pool(concurrency)
    data_list = pool.map(task_func, task_arguments)

    format_processing_action_output(data_list, ctx.format)


def download_file_from_dict(d):
    ctx = d['ctx']
    if ctx.verbose:
        click.echo('>> Downloading file into %s' % d['filepath'], err=True)
    result = download_file(d['url'], d['filepath'])
    click.echo('<< Downloaded file into %s' % d['filepath'], err=True)
    return result


class UnrecognizedInputTypeByExtension(Exception):
    pass


def guess_input_type(ext):
    if ext.startswith('.'):
        ext = ext.strip('.')
    if ext in [
        'jpeg', 'jpg', 'png',
    ]:
        return 'image'
    elif ext in [
        'mp4', 'mov', 'avi'
    ]:
        return 'video'
    else:
        raise UnrecognizedInputTypeByExtension('File with extension %s is given' % ext)
