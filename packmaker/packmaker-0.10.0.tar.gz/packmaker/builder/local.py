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
import shutil
import zipfile

from .base import BaseBuilder
from ..download import HttpDownloader
from ..minecraft import Minecraft

##############################################################################


class LocalBuilder (BaseBuilder):

    build_subloc = 'local'

    ##########################################################################

    def setup_build(self, parsed_args):
        super(LocalBuilder, self).setup_build(parsed_args)

        self.mods_location = self.build_location('mods')
        self.resourcepacks_location = self.build_location('resourcepacks')
        self.libs_location = self.build_location('libraries')
        self.natives_location = self.build_location('natives')
        self.assets_location = self.build_location('assets')

    ##########################################################################

    def do_build(self):
        self.downloader = HttpDownloader(self.cache_location())

        self.log.info('Copying local files ...')
        self.copy_files(files_iterator=self.packlock.yield_clientonly_files())

        self.log.info('Copying mod files ...')
        self.copy_mods(self.mods_location, self.packlock.yield_clientonly_mods())

        self.log.info('Copying resourcepack files ...')
        self.copy_resourcepacks(self.resourcepacks_location)

        mc = Minecraft(self.packlock.get_metadata('minecraft_version'))
        self.copy_minecraft_client(mc)

        modloader = self.packlock.get_modloader(self.downloader)
        if modloader is not None:
            modloader.install(self.build_location(), 'client')

    ##########################################################################

    def copy_minecraft_client(self, mc):
        mc.download_client(self.downloader.subdownloader('minecraft'))

        manifest = mc.get_version_manifest()

        # Copy the minecraft client library into place.

        cached_lib = os.path.join(self.cache_location('minecraft'), 'versions', manifest['id'], 'client.jar')
        local_lib = os.path.join(self.libs_location, 'com', 'mojang', 'minecraft', manifest['id'],
                                 'minecraft-{}-client.jar'.format(manifest['id']))

        if not os.path.exists(os.path.dirname(local_lib)):
            os.makedirs(os.path.dirname(local_lib))

        shutil.copy2(cached_lib, local_lib)

        # Copy the minecraft libraries into place.

        for lib in mc.get_libraries():
            cached_lib = os.path.join(self.cache_location('minecraft'), 'libraries', lib.get_path_local())

            if lib.must_extract():
                with zipfile.ZipFile(cached_lib, 'r') as extractedlib:
                    for name in extractedlib.namelist():
                        excluded = False
                        for exclude in lib.extract_excludes():
                            if name.startswith(exclude):
                                excluded = True
                                break
                        if excluded:
                            continue
                        extractedlib.extract(name, path=self.natives_location)

            else:
                localdir = os.path.join(self.libs_location, os.path.dirname(lib.get_path_local()))
                if not os.path.exists(localdir):
                    os.makedirs(localdir)

                local_lib = os.path.join(self.libs_location, lib.get_path_local())
                shutil.copy2(cached_lib, local_lib)

        # Copy the minecraft assets into place.

        assetIndexDir = os.path.join(self.assets_location, 'indexes')
        if not os.path.exists(assetIndexDir):
            os.makedirs(assetIndexDir)

        assetIndexFile = '{}.json'.format(manifest['assets'])

        cached_assetIndexFile = os.path.join(self.cache_location('minecraft'), 'assets', 'indexes', assetIndexFile)
        local_assetIndexFile = os.path.join(self.assets_location, 'indexes', assetIndexFile)
        shutil.copy2(cached_assetIndexFile, local_assetIndexFile)

        for key, val in mc.get_assets_index()['objects'].items():
            h = val['hash']
            path = '{}/{}'.format(h[0:2], h)

            cached_assetfile = os.path.join(self.cache_location('minecraft'), 'assets', 'objects', path)
            local_assetfile = os.path.join(self.assets_location, 'objects', path)

            if not os.path.exists(os.path.dirname(local_assetfile)):
                os.makedirs(os.path.dirname(local_assetfile))

            shutil.copy2(cached_assetfile, local_assetfile)

##############################################################################
# THE END
