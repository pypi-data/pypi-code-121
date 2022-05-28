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
import re
import requests
import zipfile

from .framew.application import OperationError
from .libraries import Library
from .modloader import ModLoader

##############################################################################


class FabricModLoader (ModLoader):

    FABRIC_META_URL = 'https://meta.fabricmc.net/v2/versions'

    #########################################################################

    def __init__(self, minecraft_version, loader_version, downloader):
        super(FabricModLoader, self).__init__(minecraft_version, loader_version, downloader)
        self.manifest = None

    #########################################################################

    def get_mainclass(self):
        manifest = self._get_fabric_manifest()
        return manifest['launcherMeta']['mainClass']['client']

    #########################################################################

    def get_launch_arguments(self):
        pass

    #########################################################################

    def get_libraries(self, side=None):
        dependents = []
        if side is None:
            side = 'client'
        manifest = self._get_fabric_manifest()

        for lib in ('loader', 'intermediary'):
            manifest_lib = manifest[lib]
            dependents.append(Library({'name': manifest_lib['maven'], 'url': 'https://maven.fabricmc.net/'}))

        libraries = manifest['launcherMeta']['libraries']
        for lib in libraries['common']:
            library = Library(lib)
            if library.matches(None):
                dependents.append(library)
        for lib in libraries[side]:
            library = Library(lib)
            if library.matches(None):
                dependents.append(library)
        return dependents

    #########################################################################

    def install(self, install_location, side):
        self.log.info('Installing fabric and dependent libraries ...')
        if side == 'client':
            self.install_client(install_location)
        elif side == 'server':
            self.install_server(install_location)

    def install_client(self, install_location):
        lib_location = os.path.join(install_location, 'libraries')
        if not os.path.exists(lib_location):
            os.makedirs(lib_location)
        self._install_libraries(lib_location, self.get_libraries('client'))

    def install_server(self, install_location):
        launcher_jar = os.path.join(install_location, 'fabric-server-launch.jar')
        with zipfile.ZipFile(launcher_jar, mode='w', compression=zipfile.ZIP_DEFLATED) as jarfile:

            with jarfile.open('META-INF/MANIFEST.MF', mode='w') as mf:
                mf.write('Manifest-Version: 1.0\n'.encode('utf-8'))
                mf.write('Main-Class: net.fabricmc.loader.launch.server.FabricServerLauncher\n'.encode('utf-8'))

            with jarfile.open('fabric-server-launch.properties', mode='w') as props:
                props.write('launch.mainClass=net.fabricmc.loader.launch.knot.KnotServer\n'.encode('utf-8'))

            services = {}
            for library in self.get_libraries('server'):
                downloaded_file = None
                for url in library.get_download_urls():
                    try:
                        downloaded_file = self.downloader.download_immediate(url, library.get_path())
                        break
                    except requests.exceptions.HTTPError as herr:
                        self.log.moreinfo('Failed downloading {} - {}'.format(url, herr))

                if downloaded_file is None:
                    raise OperationError('Cannot download library: {}'.format(library.get_filename()))

                with zipfile.ZipFile(downloaded_file, mode='r') as library_jar:
                    for entry in library_jar.infolist():
                        if entry.is_dir():
                            continue
                        name = entry.filename
                        if name.startswith('META-INF/services/'):
                            # service handling here
                            if name not in services:
                                services[name] = []

                            lines = []
                            with library_jar.open(name, mode='r') as serv:
                                lines = serv.readlines()

                            for line in [line.decode() for line in lines]:
                                line = re.sub('#.*$', '', line).strip()
                                if line and line not in services[name]:
                                    services[name].append(line)

                        elif name in jarfile.namelist():
                            # duplicate file. skipping ...
                            pass
                        else:
                            with library_jar.open(name, mode='r') as input:
                                with jarfile.open(name, mode='w') as output:
                                    output.write(input.read())

            # Write services
            for entry, content in services.items():
                with jarfile.open(entry, mode='w') as serv:
                    for line in content:
                        serv.write('{}\n'.format(line).encode('utf-8'))

        # fabric-server-launcher.properties file
        serverjar = os.path.join('libraries', 'com', 'mojang', 'minecraft', self.minecraft_version,
                                 'minecraft-{}-server.jar'.format(self.minecraft_version))
        with open(os.path.join(install_location, 'fabric-server-launcher.properties'), 'w') as props:
            props.write('serverJar={}\n'.format(serverjar))

    #########################################################################

    def get_server_jar_filename(self):
        return 'fabric-server-launch.jar'

    #########################################################################

    def _get_fabric_manifest(self):
        if self.manifest is None:
            manifest_url = self.FABRIC_META_URL + '/loader/{}/{}'.format(self.minecraft_version, self.loader_version)
            self.manifest = requests.get(manifest_url).json()
        return self.manifest

##############################################################################


FABRIC_LOADER_URL = "https://meta.fabricmc.net/v2/versions/loader/{}"


def calculate_fabric_version(minecraft_version, fabric_version):
    url = FABRIC_LOADER_URL.format(minecraft_version)
    loaders = requests.get(url, timeout=60).json()
    return loaders[0]['loader']['version']

##############################################################################
# THE END
