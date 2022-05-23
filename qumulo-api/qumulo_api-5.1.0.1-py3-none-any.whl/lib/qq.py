# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# qumulo_python_versions = { 3.6, latest }

import argparse
import logging
import os
import sys
import warnings

from typing import Optional, Sequence

from typing_extensions import Protocol

import qumulo
import qumulo.commands
import qumulo.lib.auth
import qumulo.lib.opts as opts
import qumulo.lib.request

from qumulo.lib import log
from qumulo.lib.auth import Credentials
from qumulo.rest_client import RestClient

USER_AGENT = 'qq'


def main_options(parser: argparse.ArgumentParser, endpoint_args: bool = True) -> None:
    parser.add_argument(
        '--chunked',
        action='store_true',
        default=qumulo.lib.request.DEFAULT_CHUNKED,
        help='Force chunked transfer encoding for requests',
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=qumulo.lib.request.DEFAULT_CHUNK_SIZE_BYTES,
        help=(
            'Set chunk size in bytes for chunked transfer encoding (default: %d)'
            % qumulo.lib.request.DEFAULT_CHUNK_SIZE_BYTES
        ),
    )
    parser.add_argument(
        '--credentials-store',
        default=None,
        help='Read and writes credentials to a custom path (default: ~/.qfsd_cred)',
    )
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--version', action='version', version=f'%(prog)s {qumulo.__version__}')
    parser.add_argument(
        '--timeout', type=int, default=None, help='Time (in seconds) to wait for response'
    )
    if endpoint_args:
        # simnode/qq_internal wants these arguments omitted
        parser.add_argument('--host', default='localhost')
        parser.add_argument('--port', type=int, default=8000)


class RestClientFactoryProtocol(Protocol):
    def __call__(
        self,
        address: str,
        port: int,
        credentials: Optional[Credentials] = None,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ) -> RestClient:
        ...


def main(args: argparse.Namespace, rest_client_factory: RestClientFactoryProtocol) -> None:
    if not logging.root.handlers:
        logging.basicConfig(format='%(message)s')

    if args.debug or args.verbose > 1:
        log.setLevel(level=logging.DEBUG)
    elif args.verbose == 1:
        log.setLevel(level=logging.INFO)

    # Allow DeprecationWarnings to be printed when using qq.
    warnings.simplefilter('default', DeprecationWarning)

    if args.credentials_store is None:
        credentials_store_path = qumulo.lib.auth.credential_store_filename()
    else:
        credentials_store_path = args.credentials_store

    credentials = qumulo.lib.auth.get_credentials(credentials_store_path)
    rest_client = rest_client_factory(
        args.host, args.port, credentials=credentials, timeout=args.timeout, user_agent=USER_AGENT
    )
    rest_client.chunked = args.chunked
    rest_client.chunk_size = args.chunk_size

    # XXX: The typing here isn't right and we're only saved because run_subcommand currently is
    # un-typed. We want to have the return type of rest_client_factory have a type that matches what
    # the command takes. Public commands take a qumulo.rest_client.RestClient, while private
    # commands take a qinternal.api.client.rest_client.RestClient, which is a subclass of
    # qumulo.rest_client.RestClient.
    opts.run_subcommand(args.subcommand, rest_client, args)


def qq_main(argv: Sequence[str], rest_client_factory: RestClientFactoryProtocol) -> int:
    try:
        parzer = argparse.ArgumentParser(description='Qumulo CLI', add_help=True)
        main_options(parzer)
        argz = opts.parse_options(parzer, argv)
        assert argz is not None

        # If no subcommand is specified, the Namespace object is returned but it is
        # missing the subcommand attribute. See https://bugs.python.org/issue9253
        if not hasattr(argz, 'subcommand'):
            parzer.print_usage()
            print('qq: error: too few arguments; try --help to find a list of usable subcommands.')
            return 1
        main(argz, rest_client_factory)

    except KeyboardInterrupt:
        print('\nCommand interrupted')
        return 1

    except qumulo.lib.request.RequestError as e:
        # When using QQ RequestError is common and expected. Only print out a
        # terse message about the error by calling pretty_str.
        print(e.pretty_str())
        return 1

    except ValueError as e:
        if os.getenv('DEBUG_CLI') or (argz is not None and argz.debug):
            print('Command error: %s' % str(e))
            raise

        print('Command error: %s' % str(e))
        return 1

    except OSError as e:
        print('Connection error: %s' % str(e))
        return 1

    return 0


def qq_main_PYTHON_ARGCOMPLETE_OK() -> int:
    """
    The entry point called when `qq` is installed with the Python SDK whl (i.e. installed via `pip`).

    Why the strange name? When a user installs `qq` from a whl file, the `qq` executable they invoke
    is a short, autogenerated Python script which invokes an entry point specified by us.

    Python-argcomplete < 1.10.1 requires the magic string PYTHON_ARGCOMPLETE_OK to be within the
    first 1024 bytes of an executable to perform completion. The easiest way to inject that string
    into the auto-generated `qq` executable is by including it in the entry point name.

    python-argcomplete 1.10.1 is able to traverse through the entry point call to find an annotation
    in the original source (e.g. here), but most OS's ship older versions (e.g. Ubuntu 20.04 ships
    1.8.1).
    """
    return qq_main(sys.argv[1:], RestClient)
