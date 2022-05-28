# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
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
import json
import os.path
import requests
import urllib.parse

from .curse.curseforge import Curseforge
from .framew.application import OperationError
from .framew.config import ConfigError
from .framew.log import getlog
from .packdef import ModDefinition, ResourcepackDefinition

##############################################################################

depend_types = ["_all_", "embeddedlib", "optional", "required", "tool", "incompatible", "include"]

release_types = ["_unknown", "release", "beta", "alpha"]


class Resolver (object):
    """
    Addon resolver logic, turning a simple addon definition from the packdef into a fully
    resolved addon object, with download urls and dependnecies resolved.
    """

    # A list of minecraft versions that are "fuzzily" equivalent, meaning that if a mod
    # specifies one version of minecraft as a dependency, the other versions should also
    # work correctly.  This helps when minecraft bumps a version up, but a version of the
    # mod is not released explicitly for the new minecraft version as there is no functional
    # code differences between them that would require a new mod release. A good example of
    # this is minecraft versions 1.16.4 and 1.16.5. Nearly all mods for the specify one of
    # these minecraft versions will also work on the other...
    fuzzy_mc_versions = [["1.16.4", "1.16.5"], ]

    def __init__(self, config, pack, fuzzy=True):
        super(Resolver, self).__init__()
        self.log = getlog()
        self.allow_fuzzy_mc_versions = fuzzy
        self.setup_api(config)
        self.setup_db(config)
        self.setup_pack(pack)

    def setup_api(self, config):
        authn_token = config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def setup_db(self, config):
        db_filename = config.get('curseforge::moddb_filename')
        if db_filename is None:
            self.log.warning('No moddb_filename parameter in configuration.'
                             ' This will force packmaker to make API calls to resolve every addon')
            self.db = None
            return

        self.log.moreinfo('Loading curseforge database ...')
        with open(db_filename, 'r') as cf:
            self.db = json.load(cf)

    def setup_pack(self, pack):
        self.mc_version = [pack.minecraft_version]
        if self.allow_fuzzy_mc_versions:
            for fuzzy in self.fuzzy_mc_versions:
                if pack.minecraft_version in fuzzy:
                    self.mc_version = fuzzy
                    break

        self.modloader = None
        if pack.forge_version is not None:
            self.modloader = 'forge'
        elif pack.fabric_version is not None:
            self.modloader = 'fabric'

        self.mod_releasetypes = pack.get_mod_releasetypes()
        self.resourcepack_releasetypes = pack.get_resourcepack_releasetypes()

        self.defined_mods = pack.get_all_mods()
        self.defined_resourcepacks = pack.get_all_resourcepacks()

    def resolve_addon(self, addon, addontype, packlock):
        self.log.moreinfo('Resolving: {}'.format(addon.slug))
        if addon.url is not None:
            # Find the addon by raw URL
            try:
                u = urllib.parse.urlparse(addon.url)
                filename = os.path.basename(u.path)
                packlock.add_resolved_addon(addon, addontype, {'fileName': filename, 'downloadUrl': addon.url})
            except ValueError:
                raise OperationError('Invalid addon url for {}'.format(addon.slug))

        else:
            # Find the addon in curseforge
            if addon.curseforgeid is not None:
                slug, name, addonid, author = self.find_addon_by_id(addon.curseforgeid, addontype)
            else:
                slug, name, addonid, author = self.find_addon_by_slug(addon.slug, addontype)
            found = self.find_addon_file(addonid, addon.version, addontype)
            if found is None:
                raise OperationError('Cannot find an addon file for {}'.format(addon.slug))
            packlock.add_resolved_addon(addon, addontype,
                                        {'projectId': addonid,
                                         'name': name,
                                         'author': author,
                                         'fileId': found['id'],
                                         'fileName': found['fileName'],
                                         'version': found['displayName'],
                                         'downloadUrl': found['downloadUrl']
                                         })
            self.check_dependencies(found['dependencies'], addon.ignoredeps, addontype, packlock)

    def check_dependencies(self, dependencies, ignoredeps, addontype, packlock):
        self.log.moreinfo("Checking for dependencies...")
        if type(ignoredeps) is str and ignoredeps == "all":
            self.log.moreinfo('  all dependencies ignored ("ingoreddeps: all")')
            return
        if len(dependencies) == 0:
            self.log.moreinfo('  no dependencies')
            return

        for dep in dependencies:
            addonid = dep['modId']
            deptype = dep['relationType']
            if deptype != 3:
                self.log.moreinfo('  ignoring dependency (id={}, type={} ({}))'.format(addonid, deptype, depend_types[deptype]))
                continue

            depslug, depname, depid, depauthors = self.find_addon_by_id(addonid, addontype)
            if depslug in ignoredeps:
                self.log.moreinfo('  Ignoring dependency: {}'.format(depslug))
                continue

            self.log.moreinfo('  Solving dependency: {}'.format(depslug))
            try:
                # search the packdef. is this addon already included?
                packlock.get_addon(depslug, addontype)
                self.log.moreinfo('  Dependent addon already resolved')
            except KeyError:
                # Not already included. Is it an already solved dependency?
                if addontype == 'mod':
                    definitions = self.defined_mods
                    addondef = ModDefinition(depslug, None)
                elif addontype == 'resourcepacks':
                    definitions = self.defined_resourcepacks
                    addondef = ResourcepackDefinition(depslug, None)
                for depdef in definitions:
                    if depdef.slug == depslug:
                        self.log.moreinfo('  Dependent addon already include in packdef')
                        break
                # Not included and not already solved: resolve this dependent addon
                else:
                    self.log.moreinfo('  Addon needs resolution: {}'.format(depslug))
                    self.resolve_addon(addondef, addontype, packlock)

    def find_addon_by_slug(self, slug, addontype):
        if self.db is not None and slug in self.db and self.db[slug]['category'] == addontype:
            return slug, \
                self.db[slug]['name'], \
                self.db[slug]['id'], \
                self.db[slug]['authors'][0]['name']
        else:
            return self.manual_addon_search(slug, addontype)

    def find_addon_by_id(self, id, addontype):
        if self.db is not None:
            for slug, entry in self.db.items():
                if entry['id'] == id and entry['category'] == addontype:
                    return entry['slug'], \
                        entry['name'], \
                        id, \
                        entry['authors'][0]['name']

        try:
            addon = self.api.get_addon(id)
        except requests.exceptions.HTTPError:
            raise OperationError('Cannot find an addon with curseforge id {}'.format(id))

        return addon['slug'], \
            addon['name'], \
            addon['id'], \
            addon['authors'][0]['name']

    def manual_addon_search(self, slug, addontype):
        self.log.warning('Cannot find addon in local db: {}. Manually searching...'.format(slug))

        if addontype == 'mod':
            classid = 6
        elif addontype == 'resourcepack':
            classid = 12
        else:
            raise Exception('unknown addontype passed to manual_addon_search()')

        searchresults = list(({'name': addon['name'], 'id': addon['id'], 'slug': addon['slug'],
                               'authors': addon['authors']}
                              for addon in self.api.yield_addons_by_criteria(gameId=432, classId=classid,
                                                                             gameVersions=self.mc_version,
                                                                             searchFilter=slug)))

        if len(searchresults) < 1:
            raise OperationError('Cannot find an addon named \'{}\''.format(slug))
        elif len(searchresults) > 1:
            self.log.warning('Multiple search results found ({}).  Looking for an exact match in results...'
                             .format(len(searchresults)))
            for sresult in searchresults:
                if sresult['slug'] == slug:
                    searchresult = sresult
                    self.log.warning('Found it! ... {} (id = {})'.format(searchresult['slug'], searchresult['id']))
                    break
            else:
                searchresult = searchresults[0]
                self.log.warning('No exact match found! Using the first one (this could be wildly wrong) ... {} (id = {})'
                                 .format(searchresult['slug'], searchresult['id']))
        else:
            searchresult = searchresults[0]
            self.log.warning('Found it! ... {} (id = {})'.format(searchresult['slug'], searchresult['id']))

        return (searchresult['slug'], searchresult['name'], searchresult['id'],
                searchresult['authors'][0]['name'])

    def find_addon_file(self, id, required_version, addontype):
        latestTimestamp = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
        addon_found = None

        # Is the required_version an integer? If so, we will use it as a curseforge file id
        try:
            rvint = int(required_version)
        except ValueError:
            rvint = None

        for addonfile in self.api.yield_addon_files(id):
            if rvint is not None:
                # exact version specified as a curseforge id. Just use it, with no additional checks
                if addonfile['id'] == rvint:
                    return addonfile

            elif required_version not in ['latest', 'latest-alpha', 'latest-beta', 'latest-release']:
                # exact version specifed.  Just use it, with no additonal checks
                if addonfile['fileName'] == required_version or \
                   addonfile['displayName'] == required_version:
                    return addonfile

            else:
                for mc_ver in self.mc_version:
                    if mc_ver in addonfile['gameVersions']:
                        break
                else:
                    continue

                if self.modloader == 'forge' and 'Fabric' in addonfile['gameVersions']:
                    continue
                elif self.modloader == 'fabric' and 'Forge' in addonfile['gameVersions']:
                    continue

                if required_version == 'latest-release' and addonfile['releaseType'] > 1:
                    continue
                if required_version == 'latest-beta' and addonfile['releaseType'] > 2:
                    continue

                if required_version == 'latest':
                    if addontype == 'mod':
                        releasetypes = self.mod_releasetypes
                    elif addontype == 'resourcepack':
                        releasetypes = self.resourcepack_releasetypes
                    else:
                        releasetypes = None
                    if releasetypes is not None:
                        if addonfile['releaseType'] == 3 and 'alpha' not in releasetypes:
                            continue
                        if addonfile['releaseType'] == 2 and 'beta' not in releasetypes:
                            continue
                        if addonfile['releaseType'] == 1 and 'release' not in releasetypes:
                            continue

                timestamp = dateutil.parser.parse(addonfile['fileDate'])
                if timestamp > latestTimestamp:
                    addon_found = addonfile
                    latestTimestamp = timestamp

        return addon_found

##############################################################################
# THE END
