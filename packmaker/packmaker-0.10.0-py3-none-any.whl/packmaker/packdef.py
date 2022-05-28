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

import os

import yaml
try:
    yamlload = yaml.full_load
except AttributeError:
    yamlload = yaml.load

from .framew.application import OperationError
from .packlock import PackLock

##############################################################################


class PackDefinition (object):

    default_releasetypes = ['alpha', 'beta', 'release']

    def __init__(self, filenames):
        super(PackDefinition, self).__init__()
        self.definition_filenames = filenames
        self.name = None
        self.title = None
        self.version = None
        self.authors = []
        self.icon = None
        self.news = None
        self.minecraft_version = None
        self.forge_version = None
        self.fabric_version = None
        self.routhio = None
        self.mods = {}
        self.resourcepacks = {}
        self.mod_releasetypes = self.default_releasetypes
        self.resourcepack_releasetypes = self.default_releasetypes
        self.files = []

    def load(self):
        for filename in self.definition_filenames:
            self.load_one(filename)

    def load_one(self, filename):
        try:
            with open(filename, 'r') as pf:
                packdict = yamlload(pf)
        except FileNotFoundError:
            raise OperationError('Cannot find pack definition file: {}'.format(filename))
        except yaml.YAMLError as err:
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                raise OperationError('Invalid pack definition file: {}\n'
                                     'Cannot parse yaml at line {}, column {}'.format(filename, mark.line+1, mark.column+1))
            raise OperationError('Invalid pack definition file:{}\nCannot parse yaml.'.format(filename))
        self.populate(packdict)

    def populate(self, packdict):
        if 'name' in packdict:
            self.name = str(packdict['name'])
        if 'title' in packdict:
            self.title = str(packdict['title'])
        if 'version' in packdict:
            self.version = str(packdict['version'])
        if 'author' in packdict:
            author = packdict['author']
            if type(author) is not list:
                self.authors.append(str(author))
            else:
                self.authors.extend(str(author) for author in packdict['author'])
        if 'authors' in packdict:
            authors = packdict['authors']
            if type(authors) is not list:
                self.authors.append(str(authors))
            else:
                self.authors.extend(str(author) for author in packdict['authors'])
        if 'icon' in packdict:
            self.icon = str(packdict['icon'])
        if 'news' in packdict:
            self.news = str(packdict['news'])
        if 'minecraft' in packdict:
            self.minecraft_version = str(packdict['minecraft'])
        if 'forge' in packdict:
            self.forge_version = str(packdict['forge'])
        if 'fabric' in packdict:
            self.fabric_version = str(packdict['fabric'])
        if 'routhio' in packdict:
            self.routhio = packdict['routhio']

        if self.forge_version is not None and self.fabric_version is not None:
            raise OperationError('both forge and fabric modloaders defined. Only one or the other is allowed.')

        if 'releasetypes' in packdict:
            if 'mods' in packdict['releasetypes']:
                self.mod_releasetypes = packdict['releasetypes']['mods']
                if type(self.mod_releasetypes) is str:
                    self.mod_releasetypes = [self.mod_releasetypes]
                for rtype in self.mod_releasetypes:
                    if rtype not in ['alpha', 'beta', 'release']:
                        raise OperationError('unknown releasetype "{}" for mods'.format(rtype))

            if 'resourcepacks' in packdict['releasetypes']:
                self.resourcepack_releasetypes = packdict['releasetypes']['resourcepacks']
                if type(self.resourcepack_releasetypes) is str:
                    self.resourcepack_releasetypes = [self.resourcepack_releasetypes]
                for rtype in self.resourcepack_releasetypes:
                    if rtype not in ['alpha', 'beta', 'release']:
                        raise OperationError('unknown releasetype "{}" for resourcepacks'.format(rtype))

        if 'mods' in packdict:
            for mod in packdict['mods']:
                if type(mod) is str:
                    slug, moddef = mod, None
                else:
                    slug, moddef = mod.popitem()
                self.mods[slug] = ModDefinition(slug, moddef)

        if 'resourcepacks' in packdict:
            for resp in packdict['resourcepacks']:
                if type(resp) is str:
                    slug, respdef = resp, None
                else:
                    slug, respdef = resp.popitem()
                self.resourcepacks[slug] = ResourcepackDefinition(slug, respdef)

        if 'files' in packdict:
            self.files.extend(packdict['files'])

    def get_mod_releasetypes(self):
        return self.mod_releasetypes

    def get_mod(self, slug):
        return self.mods[slug]

    def get_all_mods(self):
        return self.mods.values()

    def get_resourcepack_releasetypes(self):
        return self.resourcepack_releasetypes

    def get_resourcepack(self, slug):
        return self.resourcepacks[slug]

    def get_all_resourcepacks(self):
        return self.resourcepacks.values()

    def get_packlock(self):
        lockfile = os.path.splitext(self.definition_filenames[0])[0] + '.lock'
        return PackLock(lockfile)

##############################################################################


class PackElementDefinition (object):

    default_curseforgeid = None
    default_version = 'latest'
    default_url = None
    default_optional = False
    default_recommendation = 'starred'
    default_selected = False
    default_ignoredeps = []

    def __init__(self, slug, elem):
        super(PackElementDefinition, self).__init__()
        self.slug = slug
        try:
            self.populate(elem)
        except AttributeError:
            raise OperationError('{} definition is invalid: {}'.format(self.packelement_type, slug))

    def populate(self, elem):
        if elem is not None:
            self.curseforgeid = elem.get('curseforgeid', self.default_curseforgeid)
            self.version = elem.get('release', elem.get('version', self.default_version))
            self.url = elem.get('url', self.default_url)
            self.optional = elem.get('optional', self.default_optional)
            self.recommendation = elem.get('recommendation', self.default_recommendation)
            self.selected = elem.get('selected', self.default_selected)
            self.ignoredeps = elem.get('ignoreddependencies', elem.get('ignoreddeps', ModDefinition.default_ignoredeps))
        else:
            self.curseforgeid = self.default_curseforgeid
            self.version = self.default_version
            self.url = self.default_url
            self.optional = self.default_optional
            self.recommendation = self.default_recommendation
            self.selected = self.default_selected
            self.ignoredeps = self.default_ignoredeps

        if self.recommendation not in ('starred', 'avoid'):
            raise OperationError('addon recommendation for "{}" must be either "starred" or "avoid"'.format(self.slug))


class ModDefinition (PackElementDefinition):

    packelement_type = 'mod'

    default_clientonly = False
    default_serveronly = False

    def __init__(self, slug, moddef):
        super(ModDefinition, self).__init__(slug, moddef)

    def populate(self, moddef):
        super(ModDefinition, self).populate(moddef)
        if moddef is not None:
            self.clientonly = moddef.get('clientonly', ModDefinition.default_clientonly)
            self.serveronly = moddef.get('serveronly', ModDefinition.default_serveronly)
        else:
            self.clientonly = ModDefinition.default_clientonly
            self.serveronly = ModDefinition.default_serveronly


class ResourcepackDefinition (PackElementDefinition):

    packelement_type = 'resourcepack'

    def __init__(self, slug, respdef):
        super(ResourcepackDefinition, self).__init__(slug, respdef)

##############################################################################
# THE END
