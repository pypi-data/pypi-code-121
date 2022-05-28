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


from ..builder.curseforge import CurseforgeBuilder
from ..builder.local import LocalBuilder
from ..builder.pack import PackBuilder
from ..builder.server import ServerBuilder
from ..builder.routhio import RouthioBuilder
from ..framew.cmdapplication import Subcommand

##############################################################################


class BuildBase (Subcommand):
    builderclass = None

    ##########################################################################

    def setup(self):
        super(BuildBase, self).setup()
        self.builder = self.builderclass(self.config)

    ##########################################################################

    def get_cmdline_parser(self):
        parser = super(BuildBase, self).get_cmdline_parser()
        self.builder.add_cmdline_args(parser)
        return parser

    ##########################################################################

    def run_command(self, parsed_args):
        self.builder.setup_build(parsed_args)
        self.builder.do_build()

##############################################################################


class BuildPack (BuildBase):
    """
    Build a curseforge compatible modpack.
    """
    name = 'build-pack'
    builderclass = PackBuilder

##############################################################################


class BuildCurseforge (BuildBase):
    """
    Build a curseforge compatible modpack.
    """
    name = 'build-curseforge'
    builderclass = CurseforgeBuilder

##############################################################################


class BuildServer (BuildBase):
    """
    Build a server modpack.
    """
    name = 'build-server'
    builderclass = ServerBuilder

##############################################################################


class BuildRouthio (BuildBase):
    """
    Build a Routh.io compatible modpack.
    """
    name = 'build-routhio'
    builderclass = RouthioBuilder

##############################################################################


class BuildLocal (BuildBase):
    """
    Build a local installation
    """
    name = 'build-local'
    builderclass = LocalBuilder

##############################################################################
# THE END
