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
import yaml

from ..curse.curseforge import Curseforge
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog

##############################################################################


class ConvertCommand (Subcommand):
    """
    Convert a curseforge modpack's manifest to a packmaker yaml
    """

    name = 'convert'

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

    def get_cmdline_parser(self):
        parser = super(ConvertCommand, self).get_cmdline_parser()
        parser.add_argument('manifest', help='manifest json file')
        parser.add_argument('packdef', nargs='?', default='packmaker.yml', help='output packdef file')
        return parser

    def setup_command(self, arguments):
        self.setup_api()
        self.setup_db()

    def run_command(self, arguments):
        log = getlog()
        log.info('Reading curseforge manifest file ...')
        with open(arguments.manifest, 'r') as mf:
            manifest = json.load(mf)

        packdef = {'name': manifest['name'],
                   'title': manifest['name'],
                   'version': manifest['version'],
                   'authors': [manifest['author']],
                   'minecraft': manifest['minecraft']['version'],
                   'forge': manifest['minecraft']['modLoaders'][0]['id'].split('-', 1)[1],
                   'mods': [],
                   'resourcepacks': [],
                   'files': []}

        log.info('Looking up addons ...')
        for addon in manifest['files']:
            slug = None
            project_id = addon['projectID']
            file_id = addon['fileID']

            addon = self.api.get_addon(project_id)
            slug = addon['slug']
            log.moreinfo('  {}'.format(slug))
            if slug is None:
                log.warn('  !! Cannot find a project with id {}'.format(project_id))
                continue
            addonfile = self.api.get_addon_file(project_id, file_id)
            if addonfile is None:
                log.warn('  || Cannot find the correct version of addon: {} (fileID = {})'.format(slug, file_id))
                continue

            categoryId = int(addon['categorySection']['gameCategoryId'])
            if categoryId == 6:
                packdef['mods'].append({slug: {'version': addonfile['fileName']}})
            elif categoryId == 12:
                packdef['resourcepacks'].append({slug: {'version': addonfile['fileName']}})

        if 'overrides' in manifest:
            packdef['files'].append({'location': manifest['overrides']})

        log.info('Writing out packdef file: {} ...'.format(arguments.packdef))
        with open(arguments.packdef, 'w') as pf:
            yaml.safe_dump(packdef, stream=pf, indent=2, default_flow_style=False)

##############################################################################
# THE END
