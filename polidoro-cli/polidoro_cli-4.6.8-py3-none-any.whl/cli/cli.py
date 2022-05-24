import copy
import inspect
import os
import re
import subprocess
from argparse import SUPPRESS
from collections import defaultdict, ChainMap
from importlib import import_module
from multiprocessing import Process, Pipe
from string import Template
from subprocess import Popen, PIPE

import sys
import yaml

from polidoro_argument import Command


# Merge config1 onto config2
def merge_configuration(config1, config2):
    default_configuration = config1.get('default_configuration', {})
    for config_name, default_config in default_configuration.items():
        if config_name in config2:
            if isinstance(config2[config_name], list):
                config2[config_name].extend(default_config)
        else:
            config2[config_name] = default_config


# noinspection PyUnresolvedReferences
class CLI:
    """
    Class to create CLI commands
    """
    _processes = []
    _parent_conn, _child_conn = Pipe()
    raise_argument_error = True
    commands = None

    @classmethod
    def get_attribute(cls, name, default=None):
        return getattr(cls, name, default)

    @classmethod
    def print_if_has_message(cls, command_name, message_key):
        command_config = cls.commands.get(command_name, {})
        if isinstance(command_config, dict):
            messages = ChainMap(*command_config.get('messages', {}))
            message = messages.get(message_key)
            if message:
                print(message)

    @classmethod
    def get_interceptors(cls, method_name):
        interceptors = []
        for name, interceptor in vars(cls).items():
            value = cls.get_attribute(name)
            if name.endswith('_interceptor') and (
                    name.startswith(f'method_{method_name}') or not name.startswith('method_')) and (
                    isinstance(value, (staticmethod, classmethod)) or
                    inspect.isfunction(value) or
                    inspect.ismethod(value)):
                interceptors.append(value)
        return interceptors

    @classmethod
    def _replace_args(cls, command, name, *args, **kwargs):
        args = list(args)
        for command_interceptor in cls.get_interceptors(name):
            command, args, kwargs = command_interceptor(command, args, kwargs)

        method_args = cls._args[name]
        for arg_name in method_args:
            if arg_name not in kwargs:
                arg_name = re.sub(r'^\*', '', arg_name)
                kwargs[arg_name] = args.pop() if args else ''

        cls.get_attribute('environment', {}).update(cls._envs.get(name, {}))

        kwargs = {k: '' if v is None else v for k, v in kwargs.items()}

        return ' '.join(a for a in [Template(command).safe_substitute(**kwargs)] + args if a != '')

    @classmethod
    def _build_args(cls, method_name, args, named_args=None):
        def get_arg_and_config(_arg):
            _arg, _config = list(_arg.items())[0]
            if _config:
                if 'const' in _config:
                    for k, v in _config.items():
                        if v:
                            _eval = re.search(r'eval\((.*)\)', v)
                            if _eval:
                                _config[k] = eval(next(iter(_eval.groups())))
            return _arg, copy.deepcopy(_config)

        args_signature = []
        include_remainder = True
        if args:
            for arg in args:
                if isinstance(arg, dict):
                    arg, config = get_arg_and_config(arg)
                    args_signature.append(f'_{arg}={config or None}')
                    cls._args[method_name].append(arg)
                else:
                    args_signature.append(arg)
                    cls._args[method_name].append(arg)
                include_remainder &= cls._args[method_name][-1][0] != '*'

        if include_remainder:
            args_signature.append('*_remainder')

        if named_args:
            for arg in named_args:
                arg, config = get_arg_and_config(arg)
                alias = config.pop('alias', None)
                if alias:
                    cls.arguments_aliases[method_name][arg] = alias
                args_signature.append(f'{arg}={config or None}')
                cls._args[method_name].append(arg)

        return dict(
            args_signature=', '.join(args_signature),
            args_to_replace=', '.join([re.sub(r'(_?)(.*)=.*', '\\2=\\1\\2', a) for a in args_signature]),
        )

    @classmethod
    def _create_command_method(cls, command=None, **config):
        template = """def $name(cls, $args_signature):
            cls.print_if_has_message('$name', 'start')
            try:
                for cmd in $commands:
                        cls.execute(cls._replace_args(cmd, '$name', $args_to_replace),
                                include_default_command=$include_default_command,
                                show_cmd=$show_cmd,
                                exit_on_fail=$exit_on_fail
                        )
            except:
                cls.print_if_has_message('$name', 'error')
                raise
            cls.print_if_has_message('$name', 'finish')
"""
        if isinstance(command, list):
            commands = command
        else:
            commands = [command]

        config.setdefault('include_default_command', True)
        config.setdefault('show_cmd', True)
        config.setdefault('exit_on_fail', True)

        name = config['name']
        environment = config.get('environment')
        if environment:
            cls._envs[name] = {k: str(v) for k, v in environment.items()}

        for interceptor in config.pop('interceptors', []):
            interceptor_name, interceptor_config = list(interceptor.items())[0]

            cls.set_interceptor(f'method_{name}_{interceptor_name}', interceptor_config)

        command_help = config.get('help')
        if name == 'default_command':
            command_help = SUPPRESS
            config['include_default_command'] = False
        elif not command_help:
            default_cmd = cls.get_default_command()
            _commands = commands[:]
            if default_cmd and config['include_default_command']:
                _commands = [f'{default_cmd} {cmd}' for cmd in _commands]
            command_help = 'Run "%s"' % ' && '.join(_commands)

        command_method_str = Template(template).substitute(
            commands=commands,
            **cls._build_args(name, config.pop('arguments', []), config.pop('named_arguments', [])),
            **config)

        # noinspection BuiltinExec
        exec(command_method_str)
        command_method = locals()[name]
        setattr(command_method, '__qualname__', '%s.%s' % (cls.__qualname__, name))
        setattr(command_method, '__objclass__', cls)
        setattr(command_method, 'command', ';'.join(commands))
        setattr(cls, name, command_method)
        class_method = classmethod(cls.get_attribute(name, command_method))
        setattr(cls, name, class_method)

        aliases = config.pop('alias', [])
        if aliases and not isinstance(aliases, list):
            aliases = [aliases]

        Command(
            help=command_help,
            aliases=aliases,
            arguments_aliases=cls.get_attribute('arguments_aliases', {}).get(name)
                )(cls.get_attribute(name))

    @classmethod
    def set_interceptor(cls, name_, config_):
        def _interceptor(command_, args, kwargs):
            condition = config_.get('condition', 'True')
            try:
                condition = Template(condition).substitute(**{k: None if v is None else f'"{v}"' for k, v in kwargs.items()})
            except KeyError:
                condition = 'False'
            if eval(condition):
                command_ = Template(config_['command']).safe_substitute(
                    command=command_,
                    **kwargs
                )
            return command_, args, kwargs

        setattr(cls, f'{name_}_interceptor', _interceptor)

    @staticmethod
    def create_yml_commands(cli):
        class_name = cli.pop('name')
        cls = CLI.get_or_create_class(class_name)

        for interceptor in cli.pop('interceptors', []):
            name, config = list(interceptor.items())[0]

            cls.set_interceptor(name, config)

        for key, value in cli.items():
            if key == 'alias':
                key = 'aliases'
                value = [value]
            setattr(cls, key, value)

        commands = []
        for command_alias, config in cli.get('commands', {}).items():
            if isinstance(config, dict):
                command = config['command']
            else:
                command = config
                config = {}

            merge_configuration(cli, config)

            config.update(name=command_alias, command=command)

            if command_alias == 'default_command':
                commands.insert(0, config)
            else:
                commands.append(config)

        setattr(cls, '_args', defaultdict(list))
        setattr(cls, '_envs', defaultdict(list))
        setattr(cls, 'arguments_aliases', defaultdict(dict))
        if not hasattr(cls, 'help'):
            setattr(cls, 'help', class_name + ' CLI commands')
        for cmd_dict in commands:
            cls._create_command_method(**cmd_dict)

        return cls

    @staticmethod
    def get_or_create_class(class_name):
        return getattr(sys.modules.get(class_name.lower()), class_name,
                       getattr(sys.modules.get(class_name.lower() + '_cli'), class_name,
                               type(class_name, (CLI,), {})))

    @classmethod
    def get_default_command(cls):
        return getattr(cls.get_attribute('default_command'), 'command', None)

    @classmethod
    def execute(cls, command, exit_on_fail=True, capture_output=False,
                show_cmd=True, sync=True, include_default_command=False):
        """
        Run a shell command

        :param command: command as string
        :param exit_on_fail: If True, exit script if command fails
        :param capture_output: Return the command output AND not print in terminal
        :param show_cmd: Show command in terminal
        :param sync: If runs the command synchronously
        :param include_default_command: To include the default command in the command
        :return: subprocess.CompletedProcess
        """
        if include_default_command:
            default_command = cls.get_default_command()
            if default_command:
                if '$default_command' in command:
                    command = Template(command).substitute(default_command=default_command)
                else:
                    command = f'{default_command} {command}'
        else:
            command = command.replace('$default_command ', '')

        os.environ.update(cls.get_attribute('environment', {}))

        if show_cmd:
            print('+ %s' % Template(command).safe_substitute(os.environ).strip())

        if capture_output:
            std = PIPE
        else:
            std = None

        if not os.environ.get('CLI_TEST'):
            p = CLI.start_process(command, std)
            if sync:
                error, returns = CLI.wait_processes_to_finish()
                ret = list(returns.values())[0]

                if exit_on_fail and error:
                    exit(error)
                return ret['outs'], ret['errs']
            return p.pid

    @staticmethod
    def start_process(command, std):
        def async_run(conn, _command, _std):
            # noinspection SubprocessShellMode
            proc = Popen('exec ' + _command, shell=True, text=True, stdout=_std, stderr=_std, env=os.environ)
            try:
                outs, errs = proc.communicate()
            except KeyboardInterrupt:
                proc.terminate()
                print('Waiting until process terminate')
                proc.wait()
                outs, errs = proc.communicate()
                proc.returncode = 1

            conn.send([os.getpid(), bool(proc.returncode), outs, errs])

        p = Process(target=async_run, args=(CLI._child_conn, command, std))
        CLI._processes.append(p)
        p.start()
        return p

    @staticmethod
    def wait_processes_to_finish():
        returns = defaultdict(dict)
        error = False
        while CLI._processes:
            p = CLI._processes.pop()
            p.join()
            p_pid, c_error, c_outs, c_errs = CLI._parent_conn.recv()
            returns[p_pid] = dict(error=c_error, outs=c_outs, errs=c_errs)
            error |= c_error

        return error, returns

    @staticmethod
    def get_processes_status():
        status = {}
        for p in CLI._processes:
            status[p.pid] = p.is_alive()
        return status


@Command(help='Create suggested aliases')
def create_aliases(*remainders, **kwargs):  # noqa: C901
    bashrc_filename = os.path.expanduser('~/.bashrc')
    cli_aliases_filename = '~/.cli_aliases'
    with open(bashrc_filename, 'r') as bashrc_file:
        read = bashrc_file.read()
        if cli_aliases_filename not in read:
            with open(bashrc_filename, 'a+') as bashrc_file_write:
                print(f'Creating import "{cli_aliases_filename}" in {bashrc_filename}')
                bashrc_file_write.write(f'''
# include polidoro_cli_aliases if it exists
if [[ -f {cli_aliases_filename} ]]; then
    . {cli_aliases_filename}
fi
''')

    clis = {c.__name__: c for c in CLI.__subclasses__()}

    cli_aliases_filename = os.path.expanduser(cli_aliases_filename)
    aliases = {}
    for cli_name, cli in clis.items():
        cli_alis = cli.get_attribute('alias')
        if cli_alis:
            aliases[cli_alis] = cli_name.lower()

    for cmd_qualname, cmd in Command._commands.items():
        cli, _, cmd_name = cmd_qualname.partition('.')
        if cmd_name == 'default_command':
            continue
        cli_alias = getattr(clis.get(cli), 'alias', None)
        if cli_alias:
            cmd_alias = cmd.kwargs.get('aliases')
            if cmd_alias:
                cmd_alias = cmd_alias[0]
            else:
                cmd_alias = cmd_name
            alias = f'{cli_alias}{cmd_alias}'
            aliases[alias] = f'{cli.lower()} {cmd_alias}'
    with open(cli_aliases_filename, 'w') as cli_aliases_file:

        for alias, cmd in aliases.items():
            txt = f"alias {alias}='cli {cmd}'"
            print(f'Creating alias -> {txt}')
            cli_aliases_file.write(txt + '\n')

    print('Run "source ~/.bashrc"')


def read_yaml(file_name):
    with open(file_name) as file:
        return yaml.safe_load(file)


def load_clis(cli_dir):
    sys.path.insert(0, cli_dir)
    clis_py = []
    clis_cli = []
    clis_yaml = []
    for file in os.listdir(cli_dir):
        full_path = os.path.join(cli_dir, file)
        if os.path.isfile(full_path):
            if file.endswith('.yml') or file.endswith('.yaml'):
                clis_yaml.append(read_yaml(full_path))
            elif file.endswith('.py'):
                clis_py.append(file.replace('.py', ''))
            elif file.endswith('.cli'):
                clis_cli.append(full_path)

    # Load all <CLI>.py
    for py in clis_py:
        module = import_module(py)
        for name, var in vars(module).items():
            if isinstance(var, type) and issubclass(var, CLI):
                globals()[name] = var

    # Load all <CLI>.yml/yaml
    for cli in clis_yaml:
        cls = CLI.create_yml_commands(cli)
        if cls.__name__ not in globals():
            globals()[cls.__name__] = cls


def get_cli(cli_name):
    for name, obj in globals().items():
        if cli_name.lower() in [name.lower()] + getattr(obj, 'aliases', []):
            return obj


def import_dependency(package, package_pip_name=None):
    try:
        return import_module(package)
    except ModuleNotFoundError as mnfe:
        if package in str(mnfe):
            package_pip_name = package_pip_name or package
            print(f'This command need the module "{package_pip_name}".')
            if input(f'Install "{package_pip_name}"?[Y/n]: ').lower() in ['', 'y']:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_pip_name])
                return import_dependency(package)
            exit(1)
