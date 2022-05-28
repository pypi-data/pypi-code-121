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

import os.path
import platform

from .framew.application import OperationError

##############################################################################


class Library (object):

    GENERIC_FALLBACK_MAVEN_BASE_URLS = ['https://libraries.minecraft.net/',
                                        'https://files.minecraftforge.net/maven/',
                                        'https://repo1.maven.org/maven2/']

    def __init__(self, library):
        super(Library, self).__init__()
        self.library = library
        parts = self.library['name'].split(':')
        self.group, self.artifact, self.version = parts[:3]
        self.type = parts[3] if len(parts) >= 4 else None
        self.extension = 'jar'
        if '@' in self.version:
            self.version, self.extension = self.version.split('@', 1)

        self.native = platform.system().lower()
        if self.native == 'darwin':
            self.native = 'osx'

        arch = platform.architecture()[0]
        if arch == '64bit':
            self. arch = '64'
        elif arch == '32bit':
            self.arch = '32'
        else:
            raise OperationError('Unknown architecure. Please report this! {}'.format(arch))

    def get_native_string(self):
        if 'natives' in self.library:
            ns = self.library['natives'][self.native]
            return ns.replace('${arch}', self.arch)
        return None

    def get_filename(self):
        nativestring = self.get_native_string()
        if nativestring:
            return '{}-{}-{}.{}'.format(self.artifact, self.version, nativestring, self.extension)
        elif self.type is not None:
            return '{}-{}-{}.{}'.format(self.artifact, self.version, self.type, self.extension)
        return '{}-{}.{}'.format(self.artifact, self.version, self.extension)

    def get_path(self):
        if 'path' in self.library:
            return self.library['path']

        if 'downloads' in self.library:
            nativestring = self.get_native_string()
            if nativestring:
                return self.library['downloads']['classifiers'][nativestring]['path']
            else:
                return self.library['downloads']['artifact']['path']

        return '{}/{}/{}/{}'.format(self.group.replace('.', '/'),
                                    self.artifact,
                                    self.version,
                                    self.get_filename())

    def get_path_local(self):
        path = self.get_path()
        return os.path.join(*path.split('/'))

    def get_download_url(self):
        if 'downloads' in self.library:
            nativestring = self.get_native_string()
            if nativestring:
                return self.library['downloads']['classifiers'][nativestring]['url'] or None
            else:
                return self.library['downloads']['artifact']['url'] or None
        if 'url' in self.library:
            return '{}{}'.format(self.library['url'], self.get_path())
        return None

    def get_download_urls(self):
        urls = []
        ref_url = self.get_download_url()
        if ref_url is not None:
            urls.append(ref_url)
        for urlbase in self.GENERIC_FALLBACK_MAVEN_BASE_URLS:
            urls.append('{}{}'.format(urlbase, self.get_path()))
        return urls

    def get_artifact(self):
        return '{}:{}'.format(self.group, self.artifact)

    def matches(self, environment):
        if 'rules' not in self.library:
            return True

        allow = False
        for rule in self.library['rules']:
            if self.matches_rule(rule, environment):
                allow = rule['action'] == 'allow'
        return allow

    def matches_rule(self, rule, environment):
        if 'os' in rule:
            return rule['os']['name'] == self.native
        return True

    def must_extract(self):
        return 'natives' in self.library

    def extract_excludes(self):
        excludes = []
        if 'extract' in self.library and 'exclude' in self.library['extract']:
            excludes = self.library['extract']['exclude']
        return excludes

##############################################################################
# THE END
