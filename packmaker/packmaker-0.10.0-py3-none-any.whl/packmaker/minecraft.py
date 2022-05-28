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
import requests

from .framew.application import OperationError
from .framew.log import getlog
from .libraries import Library

##############################################################################


class Minecraft (object):

    VERSION_MANIFEST_URL = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

    ASSETS_BASE_URL = 'http://resources.download.minecraft.net/'

    def __init__(self, minecraft_version):
        super(Minecraft, self).__init__()
        self.minecraft_version = minecraft_version
        self.manifest = None
        self.assetsindex = None
        self.log = getlog()

    def get_version_manifest(self):
        if self.manifest is None:
            self.download_version_manifest()
        return self.manifest

    def get_assets_index(self):
        if self.assetsindex is None:
            self.download_assets_index()
        return self.assetsindex

    def download_client(self, downloader):
        self.log.info('Downloading minecraft client ...')
        self.download_client_jar(downloader)
        self.log.info('Downloading minecraft client libraries ...')
        self.download_libraries(downloader)
        self.log.info('Downloading minecraft client assets ...')
        self.download_assets(downloader)

    def download_server(self, downloader):
        self.log.info('Downloading minecraft server ...')
        self.download_server_jar(downloader)
        self.log.info('Downloading minecraft server libraries ...')
        self.download_libraries(downloader)

    def get_libraries(self):
        m = self.get_version_manifest()
        libs = []
        for lib in m['libraries']:
            library = Library(lib)
            if library.matches(None):
                libs.append(library)
        return libs

    def get_launch_arguments(self):
        m = self.get_version_manifest()
        if 'arguments' in m:
            return ' '.join([arg for arg in m['arguments']['game'] if type(arg) == str])
        elif 'minecraftArguments' in m:
            return m['minecraftArguments']

    def get_mainclass(self):
        version_info = self.get_version_manifest()
        return version_info['mainClass']

    ##########################################################################

    def download_version_manifest(self):
        manifesturl = None
        meta = requests.get(self.VERSION_MANIFEST_URL).json()
        for version in meta['versions']:
            if version['id'] == self.minecraft_version:
                manifesturl = version['url']
                break
        if manifesturl is None:
            raise OperationError('Cannot find a minecraft manifest for version {}'.format(self.minecraft_version))

        self.manifest = requests.get(manifesturl).json()

    def download_assets_index(self):
        m = self.get_version_manifest()
        assetsurl = m['assetIndex']['url']
        self.assetsindex = requests.get(assetsurl).json()

    def download_client_jar(self, downloader):
        m = self.get_version_manifest()
        clienturl = m['downloads']['client']['url']

        localdir = os.path.join('versions', m['id'])
        if not os.path.exists(os.path.join(downloader.download_dir, localdir)):
            os.makedirs(os.path.join(downloader.download_dir, localdir))

        localfile = os.path.join(localdir, 'client.jar')
        return downloader.download_immediate(clienturl, localfile)

    def download_server_jar(self, downloader):
        m = self.get_version_manifest()
        serverurl = m['downloads']['server']['url']

        localdir = os.path.join('versions', m['id'])
        if not os.path.exists(os.path.join(downloader.download_dir, localdir)):
            os.makedirs(os.path.join(downloader.download_dir, localdir))

        localfile = os.path.join(localdir, 'server.jar')
        return downloader.download_immediate(serverurl, localfile)

    def download_libraries(self, downloader):
        m = self.get_version_manifest()
        for lib in m['libraries']:
            library = Library(lib)
            if library.matches(None):
                url = library.get_download_url()
                if url is not None:
                    path = library.get_path()

                    localdir = os.path.join(downloader.download_dir, 'libraries', os.path.dirname(path))
                    if not os.path.exists(localdir):
                        os.makedirs(localdir)

                    localfile = os.path.join('libraries', path)
                    downloader.add_download(url, localfile)
        downloader.run()

    def download_assets(self, downloader):
        assets = self.get_assets_index()

        assetIndexDir = os.path.join(downloader.download_dir, 'assets', 'indexes')
        if not os.path.exists(assetIndexDir):
            os.makedirs(assetIndexDir)

        assetIndexFile = os.path.join(assetIndexDir, '{}.json'.format(self.get_version_manifest()['assets']))
        with open(assetIndexFile, 'w') as aif:
            aif.write(json.dumps(assets))

        for key, val in assets['objects'].items():
            h = val['hash']
            path = '{}/{}'.format(h[0:2], h)

            localfile = os.path.join('assets', 'objects', path)
            if not os.path.exists(os.path.join(downloader.download_dir, os.path.dirname(localfile))):
                os.makedirs(os.path.join(downloader.download_dir, os.path.dirname(localfile)))

            url = self.ASSETS_BASE_URL + path

            downloader.add_download(url, localfile)
        downloader.run()

##############################################################################


def version_as_integer(version_string):
    major, minor, micro = version_string.split('.')
    return (int(major) * 10000) + (int(minor) * 100) + int(micro)

##############################################################################
# THE END
