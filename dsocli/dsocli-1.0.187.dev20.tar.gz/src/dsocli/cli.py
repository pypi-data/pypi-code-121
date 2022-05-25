from dataclasses import replace
import sys
import os
import platform
from turtle import pen
import click
import re
import yaml
import glob
from stdiomask import getpass
from .constants import *
from .cli_constants import *
from .exceptions import DSOException
from .configs import Config, ConfigOrigin, ConfigService
import dsocli.logger as logger
from .parameters import Parameters
from .secrets import Secrets
from .templates import Templates
from .packages import Packages
from .releases import Releases
from .networks import Networks
from .click_extend import *
from click_params import RangeParamType
from .cli_utils import *
from .file_utils import *
from .pager import Pager
from .editor import Editor
from .version import __version__
from pathlib import Path
from .dict_utils import *
from .settings import *
from .contexts import ContextScope

modify_click_usage_error()

default_ctx = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=default_ctx)
def cli():
    """DSO CLI"""
    pass


@cli.group(context_settings=default_ctx)
def config():
    """
    Manage DSO application configuration.
    """
    pass


@cli.group(context_settings=default_ctx)
def parameter():
    """
    Manage parameters.
    """
    pass


@cli.group(context_settings=default_ctx)
def secret():
    """
    Manage secrets.
    """
    pass



@cli.group(context_settings=default_ctx)
def template():
    """
    Manage templates.
    """
    pass


@cli.group(context_settings=default_ctx)
def package():
    """
    Manage build packages.
    """
    pass


@cli.group(context_settings=default_ctx)
def release():
    """
    Manage deployment releases.
    """
    pass

@cli.group(context_settings=default_ctx)
def network():
    """
    Manage IP networks.
    """
    pass



# @network.group(context_settings=default_ctx)
# def subnet_plan():
#     """
#     Manage subnet plan.
#     """
#     pass

# @cli.group(context_settings=default_ctx)
# def provision():
#     """
#     Provision resources.
#     """
#     pass

# 

# @cli.group(context_settings=default_ctx)
# def deploy():
#     """
#     Deploy releases.
#     """
#     pass



@cli.command('version', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['version'])
def version():
    """
    Display version details.
    """
    click.echo(f"DSO CLI: {__version__}\nPython: {platform.sys.version}")




@command_doc(CLI_COMMANDS_HELP['parameter']['add'])
@parameter.command('add', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['add'])
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def add_parameter(key, value, stage, global_scope, namespace_scope, input, format, verbosity, config_override, working_dir):
    
    parameters = []
    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, parameters

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            validate_none_provided([key, value], ["KEY", "VALUE"], ["'-i' / '--input'"])
            parameters = read_data(input, 'Parameters', ['Key', 'Value'], format)

            ### eat possible enclosing (double) quotes when source is file, stdin has already eaten them!
            if format == 'compact': 
                for param in parameters:
                    param['Value'] = no_enclosing_quotes(param['Value'])

        ### no input file
        else:
            validate_provided(key, "'KEY'")
            if not value:
                Logger.warn("Null was taken as value.")
            # validate_provided(value, "'VALUE'")
            parameters.append({'Key': key, 'Value': value})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in parameters]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(parameters) == 0:
            Logger.warn("No parameter provided to add.")
        else:
            for param in parameters:
                success.append(Parameters.add(param['Key'], param['Value']))
                pending.remove(param['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if parameters:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['parameter']['list'])
@parameter.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['list'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['parameter']['uninherited'])
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.argument('filter', required=False, metavar='<regex>')
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='compact', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_parameter(stage, uninherited, filter, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'compact' and (query or query_all):
            Logger.warn("Query customizaion was ignored, becasue output format is 'compact'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Parameters: Parameters[*].{Key: Key, Value: Value, Stage: Stage, Scope: Scope}}'
        query = validate_query_argument(query, query_all, defaultQuery)
        
        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Parameters.list(uninherited, filter)
        if len(result['Parameters']) == 0:
            Logger.warn("No parameter found.")

        output = format_data(result, query, format, mainkeys=['Key', 'Value'])
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['parameter']['get'])
@parameter.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['get'])
@click.argument('key', required=True)
@click.option('--revision', metavar='<revision-id', required=False, help=CLI_PARAMETERS_HELP['parameter']['revision'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'text']), default='text', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_parameter(key, stage, global_scope, namespace_scope, revision, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'text' and (query or query_all):
            raise DSOException("Query cannot be customised using '-q'/'--query' or '-a'/'--query-all', becasue output format is 'text'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Value: Value}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Parameters.get(key, revision)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['parameter']['edit'])
@parameter.command('edit', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['edit'])
@click.argument('key', required=True)
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def edit_parameter(key, stage, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        ### always edit raw (not rendered) values, e.g. in compact/v1 providers
        result = Parameters.get(key, uninherited=True, rendered=False)
        if result:
            value = format_data(result, 'Value', 'text')
            from tempfile import NamedTemporaryFile
            ### this code was nicer, but throws permission denided exception on Windows!
            # with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
            #     tf.write(value)
            #     tf.flush()
            #     value, changed = Editor.edit(tf.name)
            tf = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
            try:
                tf.write(value)
                tf.flush()
                value, changed = Editor.edit(tf.name)
            finally:
                tf.close()
                os.unlink(tf.name)
            if changed:
                Parameters.add(key, value)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key, Config.get_namespace(ContextMode.Target), Config.get_application(ContextMode.Target), Config.get_stage(ContextMode.Target, short=True), Config.scope))


    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['parameter']['history'])
@parameter.command('history', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['history'])
@click.argument('key', required=True)
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def history_parameter(key, stage, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query
        
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Parameters.history(key)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['parameter']['delete'])
@parameter.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['parameter']['delete'])
@click.argument('key', required=False)
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_parameter(key, stage, global_scope, namespace_scope, input, format, verbosity, config_override, working_dir):

    parameters = []

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, parameters

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            parameters = read_data(input, 'Parameters', ['Key'], format)
        ### no input file
        else:
            validate_provided(key, "KEY")
            parameters.append({'Key': key})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in parameters]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(parameters) == 0:
            Logger.warn("No parameter provided to delete.")
        else:
            for parameter in parameters:
                success.append(Parameters.delete(parameter['Key']))
                pending.remove(parameter['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if parameters:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['secret']['add'])
@secret.command('add', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['add'])
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('--ask-password', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['secret']['ask_password'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def add_secret(key, value, stage, global_scope, namespace_scope, ask_password, input, format, verbosity, config_override, working_dir):

    secrets = []
    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, secrets, value

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            validate_none_provided([key, value], ["KEY", "VALUE"], ["'-i' / '--input'"])
            secrets = read_data(input, 'Secrets', ['Key', 'Value'], format)

            ### eat possible enclosing (double) quotes when source is file, as stdin has already eaten them!
            if format == 'compact': 
                for secret in secrets:
                    secret['Value'] = no_enclosing_quotes(secret['Value'])

        ### no input file
        else:
            ### should I ask password from stdin?
            if ask_password:
                validate_none_provided([value], ["VALUE"], ["'--ask-password'"])
                value = getpass(" Enter secret value: ")
                if not value == getpass("Verify secret value: "):
                    raise DSOException(CLI_MESSAGES['EnteredSecretValuesNotMatched'].format(format))
            if not value:
                Logger.warn("Null was taken as value.")
            secrets.append({'Key': key, 'Value': value})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in secrets]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(secrets) == 0:
            Logger.warn("No secret provided to add.")
        else:
            for secret in secrets:
                success.append(Secrets.add(secret['Key'], secret['Value']))
                pending.remove(secret['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if secrets:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['secret']['list'])
@secret.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['list'])
@click.option('-d', '--decrypt', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['secret']['decrypt'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['secret']['uninherited'])
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.argument('filter', required=False, metavar='<regex>')
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='compact', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_secret(stage, global_scope, namespace_scope, uninherited, decrypt, filter, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'compact' and (query or query_all):
            Logger.warn("Query customizaion was ignored, becasue output format is 'compact'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Secrets: Secrets[*].{Key: Key, Value: Value, Scope: Scope, Context: Context}}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Secrets.list(uninherited, decrypt, filter)
        if len(result['Secrets']) == 0:
            Logger.warn("No secret found.")

        output = format_data(result, query, format, mainkeys=['Key', 'Value'])
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['secret']['get'])
@secret.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['get'])
@click.argument('key', required=True)
@click.option('--revision', metavar='<revision-id', required=False, help=CLI_PARAMETERS_HELP['parameter']['revision'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'text']), default='text', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_secret(stage, global_scope, namespace_scope, key, revision, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query
        
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'text' and (query or query_all):
            raise DSOException("Query cannot be customised using '-q'/'--query' or '-a'/'--query-all', becasue output format is 'text'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Value: Value}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Secrets.get(key, revision, decrypt=True)

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['secret']['edit'])
@secret.command('edit', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['edit'])
@click.argument('key', required=True)
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def edit_secret(key, stage, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        ### always edit raw values (rendered/decrypted), e.g. in compact/v1 providers
        result = Secrets.get(key, uninherited=True, decrypt=False)
        if result:
            value = format_data(result, 'Value', 'text')
            from tempfile import NamedTemporaryFile
            ### this code was nicer, but throws permission denided exception on Windows!
            # with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
            #     tf.write(value)
            #     tf.flush()
            #     value, changed = Editor.edit(tf.name)
            tf = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
            try:
                tf.write(value)
                tf.flush()
                value, changed = Editor.edit(tf.name)
            finally:
                tf.close()
                os.unlink(tf.name)

            if changed:
                Secrets.add(key, value)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['SecretNotFound'].format(key, Config.get_namespace(ContextMode.Target), Config.get_application(ContextMode.Target), Config.get_stage(ContextMode.Target, short=True), Config.scope))


    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['secret']['history'])
@secret.command('history', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['history'])
@click.argument('key', required=True)
@click.option('-d', '--decrypt', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['secret']['decrypt'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def history_secret(key, stage, global_scope, namespace_scope, decrypt, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Secrets.history(key, decrypt)

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['secret']['delete'])
@secret.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['secret']['delete'])
@click.argument('key', required=False)
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_secret(key, stage, global_scope, namespace_scope, input, format, verbosity, config_override, working_dir):

    secrets = []
    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, secrets

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            secrets = read_data(input, 'Secrets', ['Key'], format)
        ### no input file
        else:
            validate_provided(key, "KEY")
            secrets.append({'Key': key})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in secrets]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(secrets) == 0:
            Logger.warn("No secret provided to delete.")
        else:
            for secret in secrets:
                success.append(Secrets.delete(secret['Key']))
                pending.remove(secret['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if secrets:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)



@command_doc(CLI_COMMANDS_HELP['template']['add'])
@template.command('add', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['add'])
# @click.option('--contents', 'contents_path', metavar='<path>', required=False, type=click.Path(exists=False, file_okay=True, dir_okay=True), callback=ConfigOrigin_from_string, help=CLI_PARAMETERS_HELP['template']['contents_path'])
@click.argument('contents_path', required=False, metavar='PATH', callback=ConfigOrigin_from_string)
@click.argument('key', required=False)
@click.option('--recursive', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['template']['recursive'])
@click.option('-r', '--render-path', metavar='<path>', required=False, help=CLI_PARAMETERS_HELP['template']['render_path'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('--recursive', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['template']['recursive'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def add_template(contents_path, recursive, key, render_path, stage, global_scope, namespace_scope, input, format, verbosity, config_override, working_dir):

    templates = []
    scope = ContextScope.App

    def process_key_from_path(path):

        # if not key:
        #     if os.path.samefile(path, contents_path):
        #         return os.path.basename(path)
        #     else:
        #         return path[len(contents_path)+1:]

        result = key
        ### if ** exist in key, replace it with path dirname
        if os.path.dirname(path)[len(contents_path):]:
            result = result.replace('**', os.path.dirname(path)[len(contents_path)+1:])
        else:
            result = result.replace('**/', '')
            result = result.replace('**', '')
        ### if * exist in key, replace it with path basename
        result = result.replace('*', os.path.basename(path))
        ### fix possiblly created // to /
        result = result.replace(f'{os.sep}{os.sep}', os.sep)
        ### fix possibe trailing /
        result = re.sub(f'{os.sep}$', '', result)

        return result


    def process_render_path_from_key(key):

        # if not render_path or render_path in ['.', f'.{os.sep}']:
        #     return os.path.join(f'.{os.sep}', key)

        result = render_path
        ### if ** exist in render_path, replace it with key dirname
        if os.path.dirname(key):
            result = result.replace('**', os.path.dirname(key))
        else:
            result = result.replace('**/', '')
            result = result.replace('**', '')
        ### if * exist in key, replace it with path basename
        result = result.replace('*', os.path.basename(key))
        ### fix possiblly created // to /
        result = result.replace(f'{os.sep}{os.sep}', os.sep)
        ### fix possible trailing /
        result = re.sub(f'{os.sep}$', '', result)

        # if os.path.isabs(result):
        #     Logger.warn(CLI_MESSAGES['RenderPathNotReleative'].format(result))

        # if os.path.isdir(result):
        #     print(render_path)
        #     # raise DSOException(CLI_MESSAGES['InvalidRenderPathExistingDir'].format(result))
        #     result = os.path.join(result, key)

        ### fix possiblly created // to /
        result = result.replace(f'{os.sep}{os.sep}', os.sep)

        return result

        # if result.startswith(f".{os.sep}"):
        #     return result
        # else:
        #     return os.path.join(f".{os.sep}", result)

    def validate_command_usage():
        nonlocal working_dir, scope, contents_path, key, render_path, templates

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            # validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            validate_none_provided([contents_path], ["PATH"], ["'-i' / '--input'"])
            # validate_none_provided([render_path], ["'-r' / '--render-path'"], ["'-i' / '--input'"])
            
            templates = read_data(input, 'Templates', ['Key', 'Contents', 'RenderPath'], format)

        ### no input file
        else:
            validate_provided(contents_path, "PATH") 
            # validate_provided(key, "'KEY")
            if not key:
                key = '**/*'
        
            if os.path.isdir(contents_path):
                ### remove possible trailing /
                contents_path = re.sub(f'{os.sep}$', '', contents_path)
                if recursive:
                    globe =  f'{os.sep}**'
                else:
                    globe = f'{os.sep}*'
                final_path = contents_path + globe
            else:
                final_path = contents_path

            items = glob.glob(final_path, recursive=recursive)

            ### use the current dir as the base for render path
            if not render_path:
                # render_path = f'{Config.config_dir}{os.sep}output{os.sep}**{os.sep}*'
                render_path = f'**{os.sep}*'
            else:
                if not '*' in render_path:
                    render_path = f'{render_path}{os.sep}**{os.sep}*'

            ### remove starting / if any
            render_path = re.sub(f'^{os.sep}', '', render_path)
            if not render_path.startswith(f'.{os.sep}'):
                render_path = f'.{os.sep}' + render_path

            ### processing templates from path
            for item in items:
                if not Path(item).is_file(): continue
                if is_binary_file(item):
                    Logger.warn(f"Binary file '{item}' ignored.")
                    continue
                p = str(item)
                k = process_key_from_path(p)
                r = process_render_path_from_key(k)
                if os.path.abspath(p) == os.path.abspath(r):
                    Logger.warn(f"Render path is the same as the source path, which will casue the source file to be overwritten when rendering the template: {r}")
                templates.append({'Key': k, 'Contents': open(p, encoding='utf-8', mode='r').read(), 'RenderPath': r})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in templates]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(templates) == 0:
            Logger.warn("No template provided to add.")
        else:
            for template in templates:
                success.append(Templates.add(template['Key'], template['Contents'], template['RenderPath']))
                pending.remove(template['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if templates:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)



@command_doc(CLI_COMMANDS_HELP['template']['list'])
@template.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['list'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['template']['uninherited'])
@click.option('--include-contents', 'include_contents', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['template']['include_contents'])
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.argument('filter', required=False, metavar='<regex>')
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='compact', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_template(stage, uninherited, include_contents, filter, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'compact' and (query or query_all):
            Logger.warn("Query customizaion was ignored, becasue output format is 'compact'. Use '-f'/'--format' to change it.")

        if include_contents and not format in ['json', 'yaml']:
            raise DSOException("Contents can be included only when output format is 'json' or 'yaml'. Use '-f'/'--format' to change it.")


        if include_contents:
            defaultQuery = '{Templates: Templates[*].{Key: Key, Stage: Stage, Scope: Scope, RenderPath: RenderPath, Contents: Contents}}'
        else:
            defaultQuery = '{Templates: Templates[*].{Key: Key, Stage: Stage, Scope: Scope, RenderPath: RenderPath}}'
        query = validate_query_argument(query, query_all, defaultQuery)


        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Templates.list(uninherited, include_contents, filter)
        if len(result['Templates']) == 0:
            Logger.warn("No template found.")
        output = format_data(result, query, format, mainkeys=['Key', 'RenderPath'])
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)




@command_doc(CLI_COMMANDS_HELP['template']['get'])
@template.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['get'])
@click.argument('key', required=True)
@click.option('--revision', metavar='<revision-id', required=False, help=CLI_PARAMETERS_HELP['parameter']['revision'])
# @click.option('-p', '--path', 'include_contents', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['template']['include_contents'])
@click.option('--raw', required=False, is_flag=True, default=False, help=CLI_PARAMETERS_HELP['template']['rendered'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'text']), default='text', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_template(key, revision, raw, stage, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query
        
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if format == 'text' and (query or query_all):
            raise DSOException("Query cannot be customised using '-q'/'--query' or '-a'/'--query-all', becasue output format is 'text'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Contents: Contents}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Templates.get(key, revision, rendred=not raw)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['template']['get'])
@template.command('edit', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['edit'])
@click.argument('key', required=False)
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def edit_template(key, stage, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Templates.list(uninherited=True, include_contents=True, filter=f"^{key}$")
        if result['Templates']:
            contents = format_data(result, '{Contents: Templates[0].Contents}', 'text')
            renderPath = format_data(result, '{RenderPath: Templates[0].RenderPath}', 'text')
            from tempfile import NamedTemporaryFile
            ### this code was nicer, but throws permission denided exception on Windows!
            # with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
            #     tf.write(contents)
            #     tf.flush()
            #     contents, changed = Editor.edit(tf.name)
            tf = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
            try:
                tf.write(contents)
                tf.flush()
                contents, changed = Editor.edit(tf.name)
            finally:
                tf.close()
                os.unlink(tf.name)

            if changed:
                Templates.add(key, contents, renderPath)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['TemplateNotFound'].format(key, Config.get_namespace(ContextMode.Target), Config.get_application(ContextMode.Target), Config.get_stage(ContextMode.Target, short=True), Config.scope))

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['template']['history'])
@template.command('history', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['history'])
@click.argument('key', required=True)
@click.option('-p', '--path', 'include_contents', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['template']['include_contents'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def history_template(stage, key, include_contents, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if include_contents:
            defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Contents: Contents}}'
        else:
            defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date}}'
        query = validate_query_argument(query, query_all, defaultQuery)


    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Templates.history(key, include_contents)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['template']['delete'])
@template.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['delete'])
@click.argument('key', required=False)
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_template(key, input, format, stage, global_scope, namespace_scope, verbosity, config_override, working_dir):

    templates = []

    scope = ContextScope.App


    def validate_command_usage():
        nonlocal working_dir, scope, templates

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            templates = read_data(input, 'Templates', ['Key'], format)
        ### no input file
        else:
            validate_provided(key, "KEY")
            templates.append({'Key': key})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in templates]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(templates) == 0:
            Logger.warn("No template provided to delete.")
        else:
            for template in templates:
                success.append(Templates.delete(template['Key']))
                pending.remove(template['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if templates:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['template']['render'])
@template.command('render', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['template']['render'])
@click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def render_template(stage, filter, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)
        response = Templates.render(filter)
        if response:
            result = {'Success': response, 'Failure': []}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)





@command_doc(CLI_COMMANDS_HELP['package']['list'])
@package.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['package']['list'])
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.argument('filter', required=False, metavar='<regex>')
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_package(stage, filter, query, query_all, format, verbosity, config_override, working_dir):
    
    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{Packages: Packages[*].{Key: Key, Date: Date}}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Packages.list(filter)
        if len(result['Packages']) == 0:
            Logger.warn("No package found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['package']['get'])
@package.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['package']['get'])
@click.argument('key', required=False)
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_package(stage, verbosity, config_override, working_dir, key, query, query_all, format):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query, key

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{FilePath: FilePath}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Packages.get(key=key)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['package']['build'])
@package.command('build', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['package']['build'])
@click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'text']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def build_package(stage, verbosity, config_override, working_dir, filter, query, query_all, format):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{Key: Key}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Packages.build()
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['package']['delete'])
@package.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['package']['delete'])
@click.argument('key', required=False)
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_package(stage, verbosity, config_override, working_dir, key, input, format):

    packages = []

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, packages

        if not working_dir: working_dir = os.getcwd()


        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            packages = read_data(input, 'Packages', ['Key'], format)
        ### no input file
        else:
            packages.append({'Key': key})


    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in packages]
        Config.load(working_dir, config_override, stage, ContextScope.App)

        if len(packages) == 0:
            Logger.warn("No packages provided to delete.")
        else:
            for packages in packages:
                success.append(Packages.delete(packages['Key']))
                pending.remove(packages['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if packages:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)





@command_doc(CLI_COMMANDS_HELP['release']['list'])
@release.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['release']['list'])
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.argument('filter', required=False, metavar='<regex>')
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_release(stage, verbosity, config_override, working_dir, filter, query, query_all, format):
    
    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{Releases: Releases[*].{Key: Key, Date: Date}}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Releases.list(filter)
        if len(result['Releases']) == 0:
            Logger.warn("No release found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['release']['get'])
@release.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['release']['get'])
@click.argument('key', required=True)
@click.option('--key', 'key_option', metavar='<key>', required=False, help=CLI_PARAMETERS_HELP['release']['key'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_release(stage, verbosity, config_override, working_dir, key, query, query_all, format):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{FilePath: FilePath}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Releases.get(key=key)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['release']['create'])
@release.command('create', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['release']['create'])
@click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'text']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def create_release(stage, verbosity, config_override, working_dir, filter, query, query_all, format):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, query

        if not working_dir: working_dir = os.getcwd()


        defaultQuery = '{Key: Key}'
        query = validate_query_argument(query, query_all, defaultQuery)

        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ContextScope.App)

        result = Releases.create()
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['release']['delete'])
@release.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['release']['delete'])
@click.argument('key', required=False)
@click.option('--key', 'key_option', metavar='<key>', required=False, help=CLI_PARAMETERS_HELP['release']['key'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_release(stage, verbosity, config_override, working_dir, key, input, format):


    scope = ContextScope.App
    releases = []

    def validate_command_usage():
        nonlocal working_dir, scope, releases

        if not working_dir: working_dir = os.getcwd()


        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            releases = read_data(input, 'Releases', ['Key'], format)
        ### no input file
        else:
            releases.append({'Key': key})


    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in releases]
        Config.load(working_dir, config_override, stage, ContextScope.App)

        if len(releases) == 0:
            Logger.warn("No releases provided to delete.")
        else:
            for releases in releases:
                success.append(Releases.delete(releases['Key']))
                pending.remove(releases['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if releases:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['config']['init'])
@config.command('init', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['init'])
@click.option('--setup', is_flag=True, required=False, help=CLI_PARAMETERS_HELP['config']['setup'])
@click.option('--override-inherited', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['config']['override_inherited'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['config']['input'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def init_config(setup, override_inherited, input, global_scope, namespace_scope, verbosity, config_override, working_dir):

    init_config = None

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir, scope, init_config

        if not working_dir: working_dir = os.getcwd()
        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        if input:
            try:
                init_config = yaml.load(input, yaml.SafeLoader)
            except:
                raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format('yaml'))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        # Config.load(working_dir if working_dir else os.getcwd(),
        #                 'global' if global_scope else 'namespace' if namespace_scope else 'application',
        #                 config_override)
        Config.init(working_dir, custom_init_config=init_config, config_overrides_string=config_override, override_inherited=override_inherited)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['config']['list'])
@config.command('list', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['list'])
@click.argument('filter', required=False, metavar='<regex>')
# @click.option('--filter', required=False, metavar='<regex>', help=CLI_PARAMETERS_HELP['common']['filter'])
@click.option('-u','--uninherited', 'uninherited', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['config']['uninherited'])
@click.option('--rendered', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['config']['rendered'])
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
# @click.option('--source', required=False, type=click.Choice(['all', 'local', 'remote']), default='all', show_default=True, callback=config_source_from_string, help=CLI_PARAMETERS_HELP['config']['source'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='compact', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def list_config(filter, stage, rendered, local, remote, uninherited, query, query_all, format, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.All

    def validate_command_usage():
        nonlocal working_dir, scope, query, source

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App
        
        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

        if format == 'compact' and (query or query_all):
            Logger.warn("Query customizaion was ignored, becasue output format is 'compact'. Use '-f'/'--format' to change it.")

        defaultQuery = '{Configuration: Configuration[*].{Key: Key, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)
        
        if filter:
            try:
                re.compile(filter)
            except Exception as e:
                raise DSOException(CLI_MESSAGES['InvalidFilter'].format(repr(e)))

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage, ignore_errors=True, scope=scope)
        
        result = Config.list(uninherited=uninherited, filter=filter, rendered=rendered, source=source)

        if len(result['Configuration']) == 0:
            Logger.warn("No configuration settings found.")

        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['config']['get'])
@config.command('get', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['get'])
@click.argument('key', required=True)
@click.option('--revision', metavar='<revision-id', required=False, help=CLI_PARAMETERS_HELP['config']['revision'])
@click.option('--raw', required=False, is_flag=True, default=False, help=CLI_PARAMETERS_HELP['config']['rendered'])
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'text']), default='text', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def get_config(key, revision, raw, local, remote, stage, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.All

    def validate_command_usage():
        nonlocal working_dir, scope, query, source

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

        defaultQuery = '{Value: Value}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Config.get(key, revision=revision, rendered=not raw, source=source)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['config']['add'])
@config.command('add', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['add'])
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['config']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def add_config(key, value, local, remote, stage, input, format, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.Local
    configurations = []

    def validate_command_usage():
        nonlocal working_dir, scope, value, source, configurations

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

        if input:
            validate_none_provided([key, value], ["KEY", "VALUE"], ["'-i' / '--input'"])
            configurations = read_data(input, 'Configuration', ['Key', 'Value'], format)

            ### eat possible enclosing (double) quotes when source is file, stdin has already eaten them!
            if format == 'compact': 
                for setting in configurations:
                    setting['Value'] = no_enclosing_quotes(setting['Value'])

        ### no input file
        else:
            validate_provided(key, "'KEY'")
            if not value:
                Logger.warn("Null was taken as value.")
            # validate_provided(value, "'VALUE'")
            configurations.append({'Key': key, 'Value': value})


    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in configurations]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(configurations) == 0:
            Logger.warn("No configuration setting provided to add.")
        else:
            for setting in configurations:
                success.append(Config.add(setting['Key'], setting['Value'], source=source))
                pending.remove(setting['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if configurations:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)




@command_doc(CLI_COMMANDS_HELP['config']['delete'])
@config.command('delete', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['delete'])
@click.argument('key', required=False)
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
@click.option('-i', '--input', metavar='<path>', required=False, type=click.File(encoding='utf-8', mode='r'), help=CLI_PARAMETERS_HELP['common']['input'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv', 'compact']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
# @click.option('--global', 'global_', is_flag=True, default=False, help=CLI_PARAMETERS_HELP['config']['global'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def delete_config(key, local, remote, stage,  input, format, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.Local
    configurations = []

    def validate_command_usage():
        nonlocal working_dir, scope, configurations, source

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

        if input:
            validate_none_provided([key], ["KEY"], ["'-i' / '--input'"])
            configurations = read_data(input, 'Configuration', ['Key'], format)
        ### no input file
        else:
            validate_provided(key, "KEY")
            configurations.append({'Key': key})

    success = []
    pending = []
    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        pending = [x['Key'] for x in configurations]
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        if len(configurations) == 0:
            Logger.warn("No configuration setting provided to delete.")
        else:            
            for setting in configurations:
                success.append(Config.delete(setting['Key'], source=source))
                pending.remove(setting['Key'])

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)
    finally:
        if configurations:
            failure = []
            for key in pending:
                failure.append({'Key': key})
            result = {'Success': success, 'Failure': failure}
            output = format_data(result, '', RESPONSE_FORMAT)
            Pager.page(output)



@command_doc(CLI_COMMANDS_HELP['config']['edit'])
@config.command('edit', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['edit'])
@click.argument('key', required=True)
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def edit_config(key, local, remote, stage, global_scope, namespace_scope, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.Local

    def validate_command_usage():
        nonlocal working_dir, scope, source

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        ### always edit raw (not rendered) values, e.g. in compact/v1 providers
        result = Config.get(key, uninherited=True, rendered=False, source=source)
        if result:
            value = format_data(result, 'Value', 'text')
            from tempfile import NamedTemporaryFile
            ### this code was nicer, but throws permission denided exception on Windows!
            # with NamedTemporaryFile(mode='w', encoding='utf-8', delete=True) as tf:
            #     tf.write(value)
            #     tf.flush()
            #     value, changed = Editor.edit(tf.name)
            tf = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
            try:
                tf.write(value)
                tf.flush()
                value, changed = Editor.edit(tf.name)
            finally:
                tf.close()
                os.unlink(tf.name)
            if changed:
                Config.add(key, value, source=source)
            else:
                Logger.warn(CLI_MESSAGES['NoChanegeDetectedAfterEditing'])
        else:
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key, Config.get_namespace(ContextMode.Target), Config.get_application(ContextMode.Target), Config.get_stage(ContextMode.Target, short=True), Config.scope))

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)


@command_doc(CLI_COMMANDS_HELP['config']['history'])
@config.command('history', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['config']['history'])
@click.argument('key', required=True)
@click.option('--local', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['local'])
@click.option('--remote', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['config']['remote'])
@click.option('-a', '--query-all', required=False, is_flag=True, default=False, show_default=True, help=CLI_PARAMETERS_HELP['common']['query_all'])
@click.option('-q', '--query', metavar='<jmespath>', required=False, help=CLI_PARAMETERS_HELP['common']['query'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'csv', 'tsv']), default='json', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def history_config(key, local, remote, stage, global_scope, namespace_scope, query, query_all, format, verbosity, config_override, working_dir):

    scope = ContextScope.App
    source = ConfigOrigin.Local

    def validate_command_usage():
        nonlocal working_dir, scope, query, source
        
        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

        validate_not_all_provided([local, remote], ["'--local'", "'--remote'"])
        source = ConfigOrigin.Local if local else ConfigOrigin.Remote if remote else source

        # if local:
        #     raise DSOException(f"Local configuration does not support history.")

        defaultQuery = '{Revisions: Revisions[*].{RevisionId: RevisionId, Date: Date, Value: Value}}'
        query = validate_query_argument(query, query_all, defaultQuery)

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        result = Config.history(key, source=source)
        output = format_data(result, query, format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)



@command_doc(CLI_COMMANDS_HELP['network']['subnet'])
@network.command('subnet', context_settings=default_ctx, short_help=CLI_COMMANDS_SHORT_HELP['network']['subnet'])
@click.option('-m', '--mode', required=False, type=click.Choice(['app', 'full', 'summary']), default='app', show_default=True, help=CLI_PARAMETERS_HELP['network']['subnet_layout_mode'])
@click.option('-f', '--format', required=False, type=click.Choice(['json', 'yaml', 'compact']), default='yaml', show_default=True, help=CLI_PARAMETERS_HELP['common']['format'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-s', '--stage', metavar='<name>[/<number>]', help=CLI_PARAMETERS_HELP['common']['stage'])
@click.option('-g', '--global-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['global_scope'])
@click.option('-n', '--namespace-scope', required=False, is_flag=True, help=CLI_PARAMETERS_HELP['common']['namespace_scope'])
@click.option('--config', 'config_override', metavar='<key>=<value>,...', required=False, default='', show_default=False, help=CLI_PARAMETERS_HELP['common']['config'])
@click.option('-v', '--verbosity', metavar='<number>', required=False, type=RangeParamType(click.INT, minimum=0, maximum=8), default='5', show_default=True, help=CLI_PARAMETERS_HELP['common']['verbosity'])
@click.option('-w','--working-dir', metavar='<path>', type=click.Path(exists=True, file_okay=False), required=False, help=CLI_PARAMETERS_HELP['common']['working_dir'])
def network_subnet(stage, global_scope, namespace_scope, verbosity, config_override, working_dir, mode, format):

    scope = ContextScope.App

    def validate_command_usage():
        nonlocal working_dir

        if not working_dir: working_dir = os.getcwd()

        validate_not_all_provided([global_scope, namespace_scope], ["-g' / '--global-scope'", "'-n' / '--namespace-scope'"])
        scope = ContextScope.Global if global_scope else ContextScope.Namespace if namespace_scope else ContextScope.App

    try:
        Logger.set_verbosity(verbosity)
        validate_command_usage()
        Config.load(working_dir, config_override, stage=stage, scope=scope)

        with open(Config.network('subnetPlan'), 'r') as f:
            subnet_plan = yaml.safe_load(f)

        if mode == 'app':
            result = Networks.layout_subnet_plan(subnet_plan, filters={'plan': Config.network('plan'), 'selector': Config.network('selector')}, summary=False)
        else:
            result = Networks.layout_subnet_plan(subnet_plan, summary=(mode == 'summary'))

        output = format_data(result, '', format)
        Pager.page(output)

    except DSOException as e:
        Logger.error(e.message)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(1)
    except Exception as e:
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        Logger.fatal(msg)
        if verbosity >= logger.EXCEPTION:
            import traceback
            traceback.print_exc() ### FIXME to print to logger instead of stdout
        sys.exit(2)

