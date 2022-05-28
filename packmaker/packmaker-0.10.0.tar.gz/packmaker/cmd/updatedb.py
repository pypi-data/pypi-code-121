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

import json
import os

from ..curse.curseforge import Curseforge
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog
from ..framew.string_conversion import convert_to_bool

##############################################################################


class UpdateDbCommand (Subcommand):
    """
    Download and compile a new mods database from curseforge.
    """
    name = 'updatedb'

    batchsz = 50

    addon_categories = {'mod': 6, 'resourcepack': 12}

    def get_cmdline_parser(self):
        parser = super(UpdateDbCommand, self).get_cmdline_parser()
        parser.add_argument('--ignore-mods', action='store_true',
                            help='Do not scan for mods when updating the curseforge db')
        parser.add_argument('--ignore-resourcepacks', action='store_true',
                            help='Do not scan for resourcepacks when updating the curseforge db')
        return parser

    def setup(self):
        super(UpdateDbCommand, self).setup()
        self.log = getlog()

    def setup_api(self):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def setup_db(self):
        db_filename = self.config.get('curseforge::moddb_filename')
        if db_filename is None:
            raise ConfigError('No moddb_filename parameter in configuration')
        self.db_filename = db_filename

    def setup_ignores(self):
        self.ignore_mods = convert_to_bool(self.config.get('curseforge::ignore_mods', 'false'))
        self.ignore_resourcepacks = convert_to_bool(self.config.get('curseforge::ignore_resourcepacks', 'false'))

    def setup_command(self, arguments):
        self.setup_api()
        self.setup_db()
        self.setup_ignores()

    def run_command(self, parsed_args):
        addons = {}

        dbdir = os.path.dirname(self.db_filename)
        if dbdir not in ['', '.'] and not os.path.exists(dbdir):
            self.log.debug('Creating directory: {}'.format(dbdir))
            os.makedirs(dbdir)

        if parsed_args.ignore_mods or self.ignore_mods:
            self.log.warn('Not scanning for mod addons.  Configured to ignore mods.')
        else:
            self.log.info('Scanning for list of possible mod addons...')
            addons = self.get_addons_from_api('mod')

        if parsed_args.ignore_resourcepacks or self.ignore_resourcepacks:
            self.log.warn('Not scanning for resourcepack addons.  Configure to ignore resourcepacks.')
        else:
            self.log.info('Scanning for list of possible resourcepack addons...')
            addons.update(self.get_addons_from_api('resourcepack'))

        self.log.info('Writing addons database...')
        db = json.dumps(addons)
        with open(self.db_filename, 'w') as dbfile:
            dbfile.write(db)

        self.log.moreinfo('Done.')

    def get_addons_from_api(self, category):
        addon_dict = {}
        processedIDs = []
        for addon in self.api.yield_addons_by_criteria(gameId=432,
                                                       classId=self.addon_categories[category],
                                                       sort=2,
                                                       pageSize=UpdateDbCommand.batchsz):
            processedIDs.append(addon['id'])

        for addon in self.api.yield_addons_by_criteria(gameId=432,
                                                       classId=self.addon_categories[category],
                                                       sort=3,
                                                       pageSize=UpdateDbCommand.batchsz):
            if addon['id'] not in processedIDs:
                processedIDs.append(addon['id'])

        self.log.moreinfo('Reading individual addon information...')
        chunks = [processedIDs[i:i + UpdateDbCommand.batchsz] for i in range(0, len(processedIDs), UpdateDbCommand.batchsz)]
        for chunkIDs in chunks:
            addons = self.api.get_addons(chunkIDs)
            for addon in addons:
                if not addon:
                    continue
                addon_dict[addon['slug']] = {'id': addon['id'],
                                             'name': addon['name'],
                                             'slug': addon['slug'],
                                             'category': category,
                                             'authors': addon['authors']}
        return addon_dict

##############################################################################
# THE END
