import argparse
import configparser
import json
import logging
import os
import logging

import requests

from fiddler._version import __version__
from fiddler.archive.build_container import build_cmd, register_cmd, run_cmd
from fiddler.archive.model_cmds import execute_cmd, explain_cmd
from fiddler.utils.exceptions import CommandOptionsError

LOG = logging.getLogger(__name__)

def require_arg(args, arg_name, reason=None):
    if getattr(args, arg_name) is None:

        raise CommandOptionsError(
            'option \'{}\' is required.{}'.format(
                arg_name.replace('_', '-'), f' {reason}.' if reason else ''
            )
        )
    return getattr(args, arg_name)


# Configuration schema:
# --------------------
# [default]
# organization = my_org
# auth_key = user_bearer_key_for_API
CONFIG_FILE = '{}/.fidl/config'.format(os.environ['HOME'])


def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'default' not in config.sections():
        config['default'] = {}
    return config


def write_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as out:
        config.write(out)


def api_url(args, api_method):
    """ Returns 'endpoint/api_method/org/project/model' """
    require_arg(args, 'project')
    return '%s/%s/%s/%s/%s' % (
        args.endpoint,
        api_method,
        args.org,
        args.project,
        args.model,
    )


def print_response(resp):
    for line in resp.iter_lines():
        # filter out keep-alive new lines
        if line:
            decoded_line = line.decode('utf-8')
            LOG.info(decoded_line)


def process_response(resp):
    """
    If the response is not successful, throws an
    exception with details about the error.
    Logs the response if the succeeds.
    """
    resp_str = resp.text
    try:
        resp_str = json.dumps(json.loads(resp_str), indent=4)
    except ValueError:
        # Response is not a json we print the raw text.
        pass
    if resp.status_code == requests.codes.ok:
        logging.info('Response from the service : %s', resp_str)
    else:
        logging.error('Request failed : %s', resp_str)
        resp.raise_for_status()


# Implementation of commands


def configure_cmd(args):
    config = read_config()
    section = config['default']
    for prop in ['organization', 'auth_key', 'endpoint']:
        cur = str(section.get(prop, ''))
        new = input(f'{prop}[{cur}] = ')
        if new:
            if prop == 'organization':
                section[prop] = new.lower()
            if prop == 'auth_key':
                section[prop] = new
            if prop == 'endpoint':
                section['endpoint'] = new
    write_config(config)


def parse_args(argv=None):
    """
    Parses command line arguments and runs the sub command.
    """

    common_args = argparse.ArgumentParser(description='Common Args', add_help=False)

    # Common args:
    # TODO: default project and other credentials
    #  could be stored in something like ~/.fiddler

    common_args.add_argument('--endpoint', help=argparse.SUPPRESS)

    common_args.add_argument(
        '--org', help='Organization name. ' 'Default is read from config.'
    )

    common_args.add_argument(
        '--auth-key', help='Bearer key used to ' 'authenticate REST API requests.'
    )

    model_args = argparse.ArgumentParser(
        description='Parser for --project & --model', add_help=False
    )

    model_args.add_argument(
        '--project', required=True, help='Project name in the organization. '
    )

    model_args.add_argument('--model', required=True, help='Name of the model')

    model_args.add_argument(
        '--port', required=False, default=5100, help='Port number to use'
    )

    build_args = argparse.ArgumentParser(
        description='Parser for --source', add_help=False
    )

    build_args.add_argument('--source', required=True, help='Name of the source dir')

    build_args.add_argument(
        '--train', required=False, default=False, help='Build container for training'
    )

    parser = argparse.ArgumentParser(description='Fiddler Archive (FAR)')

    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )

    subparsers = parser.add_subparsers(
        title='Available commands', dest='command', metavar=''
    )

    # deploy command
    build_desc = 'build Fiddler Archive for the specified model'
    build_parser = subparsers.add_parser(
        'build',
        parents=[common_args, model_args, build_args],
        description=build_desc,
        help=build_desc,
    )
    build_parser.set_defaults(func=build_cmd)

    # run command

    run_desc = 'runs a Fiddler Archive'
    run_parser = subparsers.add_parser(
        'run',
        parents=[common_args, model_args],
        description=run_desc,
        help=run_desc,
    )
    run_parser.set_defaults(func=run_cmd)

    # execute command
    execute_args = argparse.ArgumentParser(
        description='Parser for --index', add_help=False
    )

    execute_args.add_argument(
        '--index', required=True, help='Index of the row to execute'
    )

    execute_args.add_argument(
        '--explanations', required=False, help='Type of explanations'
    )

    execute_desc = 'execute model wrapped in Fiddler Archive'
    execute_parser = subparsers.add_parser(
        'execute',
        parents=[common_args, model_args, execute_args],
        description=execute_desc,
        help=execute_desc,
    )
    execute_parser.set_defaults(func=execute_cmd)

    # explain command
    explain_desc = 'explain the specified row'
    explain_parser = subparsers.add_parser(
        'explain',
        parents=[common_args, model_args, execute_args],
        description=explain_desc,
        help=explain_desc,
    )
    explain_parser.set_defaults(func=explain_cmd)

    # configure command
    configure_desc = 'Update Fiddler configuration'
    configure_parser = subparsers.add_parser(
        'configure', description=configure_desc, help=configure_desc
    )
    configure_parser.set_defaults(func=configure_cmd)

    # register command

    register_args = argparse.ArgumentParser(
        description='container name', add_help=False
    )

    register_args.add_argument('--image', required=True, help='Container image')

    register_args.add_argument('--dataset', required=False, help='Name of the dataset')

    register_args.add_argument('--source', required=True, help='Name of the source dir')

    register_desc = 'Register a model on fiddler'
    register_parser = subparsers.add_parser(
        'register',
        parents=[common_args, model_args, register_args],
        description=register_desc,
        help=register_desc,
    )

    register_parser.set_defaults(func=register_cmd)

    args = parser.parse_args(argv)

    if args.command:
        try:
            # Read values configuration file for options
            # if they are not specified on cmdline.
            config = read_config()['default']
            if not args.org:
                args.org = config.get('organization', '')
                if not args.org:
                    raise CommandOptionsError(
                        '--organization option is required. '
                        'Run \'configure\' to set default organization'
                    )
            if not args.auth_key:
                args.auth_key = config.get('auth_key', '')

            if hasattr(args, 'data') and args.data:
                if args.data.startswith('@'):
                    with open(args.data[1:], 'r') as file:
                        args.data = file.read()

            if hasattr(args, 'endpoint') and args.endpoint:
                args.endpoint = args.endpoint.rstrip('/')
            else:
                args.endpoint = config.get('endpoint')

            ret = args.func(args)
            if ret is None or type(ret) != int:
                return 0
            else:
                return ret

        except CommandOptionsError as e:
            logging.error(f'{str(e)}')
            logging.error(
                f'Try `{parser.prog} {args.command} --help` for ' 'more help on usage'
            )
            return 1
        except Exception as e:
            logging.error(
                f'Command "{args.command}" failed '
                f'with the following error: {str(e)}',
                exc_info=True,
            )
            return 1
    else:
        parser.print_help()
        return 0


def main(argv=None):
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)-7s: %(message)s'
    )
    return parse_args(argv)


if __name__ == '__main__':
    exit(main())
