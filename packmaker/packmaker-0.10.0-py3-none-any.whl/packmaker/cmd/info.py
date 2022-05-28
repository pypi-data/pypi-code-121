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

from ..builder.base import BaseLockLoader
from ..framew.cmdapplication import Subcommand
from ..framew.outputter import SingleOutputter
from ..fabric import FabricModLoader
from ..forge import ForgeModLoader

##############################################################################


class InfoCommand (Subcommand):
    """
    Display information about the modpack.
    """

    name = 'info'

    def setup(self):
        super(InfoCommand, self).setup()
        self.lockloader = BaseLockLoader()
        self.outputter = SingleOutputter()

    def get_cmdline_parser(self):
        parser = super(InfoCommand, self).get_cmdline_parser()
        self.lockloader.add_cmdline_args(parser)
        self.outputter.add_argument_group(parser)
        return parser

    def run_command(self, arguments):
        self.lockloader.setup_packlocks(arguments)
        packlock = self.lockloader.packlock

        keys = []
        vals = []

        self.calc_metadata(packlock, keys, vals)
        self.calc_modloader(packlock, keys, vals)

        self.outputter.produce_output(arguments, keys, vals)

    def calc_metadata(self, packlock, keys, vals):
        metadata = packlock.get_all_metadata()
        keys.extend([k for k in metadata.keys()])
        vals.extend([v for v in metadata.values()])

    def calc_modloader(self, packlock, keys, vals):
        modloader = packlock.get_modloader(None)
        keys.append('modloader_jarfile')
        if modloader is not None:
            vals.append(modloader.get_server_jar_filename())
        else:
            vals.append("")

        keys.append('forge_jarfile')
        if isinstance(modloader, ForgeModLoader):
            vals.append(modloader.get_server_jar_filename())
        else:
            vals.append("")

        keys.append('fabric_jarfile')
        if isinstance(modloader, FabricModLoader):
            vals.append(modloader.get_server_jar_filename())
        else:
            vals.append("")
