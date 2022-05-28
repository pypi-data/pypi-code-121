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

import datetime
import dateutil.parser

from ..curse.curseforge import Curseforge
from ..builder.base import BaseLockLoader
from ..framew.application import OperationError
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog
from ..framew.outputter import ListOutputter

##############################################################################


class FindUpdatesCommand (Subcommand):
    """
    Search curseforge for newer/updated versions of addons.
    """

    name = 'findupdates'

    def setup(self):
        super(FindUpdatesCommand, self).setup()
        self.lockloader = BaseLockLoader()
        self.outputter = ListOutputter()

    def setup_api(self):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def get_cmdline_parser(self):
        parser = super(FindUpdatesCommand, self).get_cmdline_parser()
        self.lockloader.add_cmdline_args(parser)
        self.outputter.add_argument_group(parser)
        return parser

    def setup_command(self, arguments):
        self.setup_api()

    def run_command(self, parsed_args):
        self.lockloader.setup_packlocks(parsed_args)
        packlock = self.lockloader.packlock

        newaddons = []

        getlog().info('Searching for newer versions of addons ...')

        def all_addons():
            for mod in packlock.get_all_mods():
                yield mod
            for resourcepack in packlock.get_all_resourcepacks():
                yield resourcepack

        for resolvedaddon in all_addons():
            try:
                addonfile_found = None
                latestTimestamp = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
                for addonfile in self.api.get_addon_files(resolvedaddon.projectId):
                    if packlock.get_metadata('minecraft_version') not in addonfile['gameVersions']:
                        continue
                    timestamp = dateutil.parser.parse(addonfile['fileDate'])
                    if timestamp > latestTimestamp:
                        addonfile_found = addonfile
                        latestTimestamp = timestamp

                if addonfile_found is None:
                    raise OperationError('Cannot find a addon file for {}'.format(resolvedaddon.name))

                if addonfile_found['id'] != resolvedaddon.fileId:
                    newaddons.append((resolvedaddon.fileName, addonfile_found['fileName']))
            except KeyError:
                newaddons.append(('{} [NEW]'.format(resolvedaddon.name), ''))

        self.outputter.produce_output(parsed_args,
                                      ('current version', 'new version'),
                                      ((m[0], m[1]) for m in newaddons))

##############################################################################
# THE END
