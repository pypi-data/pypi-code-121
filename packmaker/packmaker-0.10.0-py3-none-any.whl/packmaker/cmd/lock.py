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

from ..framew.application import OperationError
from ..framew.cmdapplication import Subcommand
from ..framew.log import getlog
from ..fabric import calculate_fabric_version
from ..forge import calculate_forge_version
from ..packdef import PackDefinition
from ..resolver import Resolver

##############################################################################

depend_types = ["_all_", "embeddedlib", "optional", "required", "tool", "incompatible", "include"]


class LockCommand (Subcommand):
    """
    Lock the modpack. Find mod download urls, generate a packmaker.lock file.
    """

    name = 'lock'

    default_packmaker_yml = 'packmaker.yml'

    def get_cmdline_parser(self):
        parser = super(LockCommand, self).get_cmdline_parser()
        parser.add_argument('--strict', default=False, action='store_true',
                            help='enforce strict minecraft version matching')
        parser.add_argument('--no-strict', dest='strict', action='store_false',
                            help='do not enforce strict minecraft version matching [default]')
        parser.add_argument('packdef',
                            nargs='*',
                            default=[LockCommand.default_packmaker_yml],
                            help='modpack definition file')
        return parser

    def setup(self):
        super(LockCommand, self).setup()
        self.log = getlog()

    def run_command(self, parsed_args):
        self.log.info('Reading pack definition ...')
        pack = PackDefinition(parsed_args.packdef)
        pack.load()

        # warn if the main metadata fields are not defined in the packdef
        for m in ('name', 'title', 'version', 'authors', 'minecraft_version'):
            val = getattr(pack, m)
            if val is None or val == []:
                self.log.warn('No \'{}\' field defined in {}'.format(m, ', '.join(parsed_args.packdef)))

        packlock = pack.get_packlock()
        packlock.set_all_metadata(pack)

        # Calculate the Forge version
        if pack.forge_version:
            if pack.forge_version not in ['latest', 'recommended']:
                packlock.set_metadata('forge_version', pack.forge_version)
            else:
                self.log.info('Resolving forge version...')
                fversion = calculate_forge_version(pack.minecraft_version, pack.forge_version)
                if fversion is None:
                    raise OperationError('Sorry, Forge does not currently publish a "{}" version for Minecraft {}'
                                         .format(pack.forge_version, pack.minecraft_version))
                self.log.moreinfo('  {} = {}'.format(pack.forge_version, fversion))
                packlock.set_metadata('forge_version', fversion)

        # Calculate the Fabric version
        if pack.fabric_version:
            if pack.fabric_version not in ['latest', 'recommended']:
                packlock.set_metadata('fabric_version', pack.fabric_version)
            else:
                self.log.info('Resolving fabric version...')
                fversion = calculate_fabric_version(pack.minecraft_version, pack.fabric_version)
                self.log.moreinfo('  {} = {}'.format(pack.fabric_version, fversion))
                packlock.set_metadata('fabric_version', fversion)

        resolver = Resolver(self.config, pack, fuzzy=(not parsed_args.strict))

        self.log.info('Resolving mods...')
        for moddef in pack.get_all_mods():
            resolver.resolve_addon(moddef, 'mod', packlock)

        self.log.info('Resolving resourcepacks...')
        for rpdef in pack.get_all_resourcepacks():
            resolver.resolve_addon(rpdef, 'resourcepack', packlock)

        self.log.info('Adding files...')
        for filesdef in pack.files:
            packlock.add_files(filesdef)

        self.log.info('Adding extra options (if any)...')
        if pack.routhio is not None:
            packlock.add_extraopt('routhio', pack.routhio)

        self.log.info('Writing pack lock...')
        packlock.save()
        self.log.moreinfo('Done.')

##############################################################################
# THE END
