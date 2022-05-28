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
from ..framew.outputter import ListOutputter

##############################################################################


class ResourcepacksInfoCommand (Subcommand):
    """
    Display information about the resourcepacks in the modpack.
    """

    name = 'resourcepacksinfo'

    def setup(self):
        super(ResourcepacksInfoCommand, self).setup()
        self.lockloader = BaseLockLoader()
        self.outputter = ListOutputter()

    def get_cmdline_parser(self):
        parser = super(ResourcepacksInfoCommand, self).get_cmdline_parser()
        self.lockloader.add_cmdline_args(parser)
        self.outputter.add_argument_group(parser)
        return parser

    def run_command(self, arguments):
        self.lockloader.setup_packlocks(arguments)

        keys = ['Name', 'Filename']
        vals = []

        for rp in self.lockloader.packlock.get_all_resourcepacks():
            vals.append((rp.name, rp.fileName))

        self.outputter.produce_output(arguments, keys, vals)
