# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pprint
from requests.exceptions import HTTPError

from ..curse.curseforge import Curseforge
from ..framew.application import OperationError
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError

##############################################################################


class ApidebugCommand (Subcommand):
    """
    Debug curse api calls
    """

    name = 'apidebug'

    apidebug_cmds = ['get_addon',
                     'get_addons',
                     'get_addon_file',
                     'get_addon_files',
                     'get_addons_by_criteria',
                     'get_modloader_timestamp',
                     'get_modloader_list',
                     'get_modloader_info',
                     'yield_addons_by_criteria',
                     ]

    def get_cmdline_parser(self):
        parser = super(ApidebugCommand, self).get_cmdline_parser()
        parser.add_argument('command', choices=self.apidebug_cmds, help='api function')
        parser.add_argument('parameters', nargs='*', help='api function parameters')
        return parser

    def setup_command(self, _arguments):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def run_command(self, arguments):
        try:
            command = getattr(self.api, arguments.command)

            params = []
            kwparams = {}
            for param in arguments.parameters:
                if '=' in param:
                    k, v = [s.strip() for s in param.split('=', 1)]
                    if v.startswith('[') and v.endswith(']'):
                        kwparams[k] = [e.strip() for e in v[1:-1].split(',')]
                    else:
                        kwparams[k] = v
                else:
                    params.append(param)

            result = command(*params, **kwparams)
            pp = pprint.PrettyPrinter(indent=2)
            if arguments.command in ['yield_addons_by_criteria']:
                idx = 0
                for oneresult in result:
                    print("{}: ".format(idx))
                    pp.pprint(oneresult)
                    idx += 1
            else:
                pp.pprint(result)
        except TypeError as err:
            raise OperationError(err)
        except HTTPError as err:
            raise OperationError(err)

##############################################################################
# THE END
