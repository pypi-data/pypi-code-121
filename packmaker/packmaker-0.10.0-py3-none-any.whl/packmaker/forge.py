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
import os.path
import requests
import shutil
import zipfile

from .curse.curseforge import Curseforge
from .framew.application import OperationError
from .framew.log import log_subprocess
from .libraries import Library
from .minecraft import Minecraft, version_as_integer
from .modloader import ModLoader

##############################################################################


class ForgeModLoader (ModLoader):

    FORGE_REPO_URL = 'https://files.minecraftforge.net/maven/'

    INCOMPATIBLE_FORGE_VERSIONS = ['14.23.5.2851']

    V19_BUILD_THAT_CHANGED_FORGE_VERSION_PATTERN = 1886
    V1122_BUILD_THAT_CHANGED_UNIVERSAL_FILENAME = 2851

    ##########################################################################

    def __init__(self, minecraft_version, loader_version, downloader):
        super(ForgeModLoader, self).__init__(minecraft_version, loader_version, downloader)
        self.installer_jar_filename = None
        self.install_profile = None
        self.version_info = None
        self.modloader_info = None

        if self.loader_version in ForgeModLoader.INCOMPATIBLE_FORGE_VERSIONS:
            raise OperationError('Sorry. Forge version {} does not work with '.format(self.forge_version)
                                 + 'packmaker. Upgrade to a newer version if possible.')

        self.calc_full_version()

    ##########################################################################

    def calc_full_version(self):
        mver = version_as_integer(self.minecraft_version)
        if mver < 10900:
            self.full_version = '{}-{}-{}'.format(self.minecraft_version, self.loader_version, self.minecraft_version)
        elif mver < 10904:
            build_num = int(self.loader_version.split('.')[-1])
            if build_num < ForgeModLoader.V19_BUILD_THAT_CHANGED_FORGE_VERSION_PATTERN:
                self.full_version = '{}-{}-{}'.format(self.minecraft_version, self.loader_version, self.minecraft_version)
            else:
                self.full_version = '{}-{}'.format(self.minecraft_version, self.loader_version)
        else:
            self.full_version = '{}-{}'.format(self.minecraft_version, self.loader_version)

    ##########################################################################

    def get_mainclass(self):
        version_info = self._get_version_info()
        return version_info['mainClass']

    ##########################################################################

    def get_launch_arguments(self):
        version_info = self._get_version_info()
        if 'arguments' in version_info:
            return ' '.join([arg for arg in version_info['arguments']['game'] if type(arg) == str])

        elif 'minecraftArguments' in version_info:
            return version_info['minecraftArguments']

    ##########################################################################

    def get_libraries(self, side=None):
        dependents = []
        version_info = self._get_version_info()
        libraries = version_info['libraries']
        for lib in libraries:
            library = Library(lib)
            if library.matches(None):
                dependents.append(library)
        return dependents

    ##########################################################################

    def install(self, install_location, side):
        self.log.info('Installing forge and dependent libraries ...')

        lib_location = os.path.join(install_location, 'libraries')
        if not os.path.exists(lib_location):
            os.makedirs(lib_location)

        self._install_libraries(lib_location, self.get_libraries())
        self._install_libraries(lib_location, self._get_installer_libraries())
        self._run_processors(lib_location, side)

        if side == 'server':
            if version_as_integer(self.minecraft_version) < 11400:
                self.log.info('Extract universal forge jar from installer...')
                universal_jar = os.path.join(install_location, self.get_server_jar_filename())
                self._get_universal_jar(universal_jar)
            else:
                src_jarfile = os.path.join(install_location, 'libraries',
                                           'net/minecraftforge/forge/{}/forge-{}.jar'.format(self.full_version,
                                                                                             self.full_version))
                dst_jarfile = os.path.join(install_location, self.get_server_jar_filename())
                shutil.copy2(src_jarfile, dst_jarfile)

    ##########################################################################

    def get_server_jar_filename(self):
        return 'forge_server-{}.jar'.format(self.full_version)

    ##########################################################################

    def _get_installer_jar(self):
        if self.installer_jar_filename is None:
            url = '{}net/minecraftforge/forge/{}/forge-{}-installer.jar'.format(ForgeModLoader.FORGE_REPO_URL,
                                                                                self.full_version,
                                                                                self.full_version)
            self.installer_jar_filename = self.downloader.download_immediate(url)
        return self.installer_jar_filename

    ##########################################################################

    def universal_download_url(self):
        return '{}net/minecraftforge/forge/{}/forge-{}-universal.jar'.format(ForgeModLoader.FORGE_REPO_URL,
                                                                             self.full_version,
                                                                             self.full_version)

    ##########################################################################

    def _universal_filename(self):
        mc_version = version_as_integer(self.minecraft_version)
        if mc_version < 11202:
            return 'forge-{}-universal.jar'.format(self.full_version)
        elif mc_version == 11202:
            build_num = int(self.loader_version.split('.')[-1])
            if build_num >= ForgeModLoader.V1122_BUILD_THAT_CHANGED_UNIVERSAL_FILENAME:
                return 'forge-{}.jar'.format(self.full_version)
        return 'forge-{}-universal.jar'.format(self.full_version)

    #########################################################################

    def _get_universal_jar(self, filename):
        installer_filename = self._get_installer_jar()
        with zipfile.ZipFile(installer_filename, 'r') as installerjar:
            try:
                universal_filename = installerjar.getinfo(self._universal_filename())
            except KeyError:
                try:
                    universal_filename = installerjar.getinfo('maven/net/minecraftforge/forge/{}/{}'.format(
                                                              self.full_version, self._universal_filename()))
                except KeyError:
                    raise Exception('Cannot find {} in the forge jar file: {}'
                                    .format(self._universal_filename(), installer_filename))

            with open(filename, 'wb') as outjar:
                with installerjar.open(universal_filename, 'r') as injar:
                    shutil.copyfileobj(injar, outjar)

    #########################################################################

    def _get_forge_info_from_curse(self):
        if self.modloader_info is None:
            api = Curseforge(None)  # no authn_token
            self.modloader_info = api.get_modloader_info('forge-{}'.format(self.loader_version))
        return self.modloader_info

    #########################################################################

    def _get_install_profile(self):
        # First, try to get the profile from the curse api ...
        if self.install_profile is None:
            profileString = self._get_forge_info_from_curse().get('installProfileJson', None)
            if profileString is not None:
                self.install_profile = json.loads(profileString)

        # If that doesn't work, download the installer jarfile and extract
        # the profile from there ...
        if self.install_profile is None:
            installer_filename = self._get_installer_jar()
            with zipfile.ZipFile(installer_filename, 'r') as installerjar:
                with installerjar.open('install_profile.json', 'r') as installf:
                    self.install_profile = json.load(installf)

        return self.install_profile

    ##########################################################################

    def _get_version_info(self):
        # First, try to get the version info the from curse api ...
        if self.version_info is None:
            versionString = self._get_forge_info_from_curse().get('versionJson', None)
            if versionString is not None:
                self.version_info = json.loads(versionString)

        # If that doesn't work, download the installer jarfile and
        # extract the profile from there ...
        if self.version_info is None:
            installer_filename = self._get_installer_jar()
            with zipfile.ZipFile(installer_filename, 'r') as installerjar:
                try:
                    with installerjar.open('version.json', 'r') as installf:
                        self.version_info = json.load(installf)
                except KeyError:
                    install_profile = self._get_install_profile()
                    if 'versionInfo' in install_profile:
                        self.version_info = install_profile['versionInfo']

        return self.version_info

    ############################################################################

    def _get_installer_libraries(self):
        dependents = []
        install_profile = self._get_install_profile()
        if 'libraries' in install_profile:
            for lib in install_profile['libraries']:
                library = Library(lib)
                if (library.artifact == "forge"
                   and library.type is not None
                   and library.type == "universal"
                   and library.get_download_url() is None):
                    # its okay to skip the forge universal library here if it doesn't
                    # have a download url in the manifest
                    continue
                if library.matches(None):
                    dependents.append(library)
        return dependents

    ############################################################################

    def _run_processors(self, lib_location, side):
        install_profile = self._get_install_profile()
        if 'processors' not in install_profile:
            return

        self.log.info('Processing installer data ...')
        data = {}
        if 'data' in install_profile:
            for datakey, dataval in install_profile['data'].items():
                dataval = dataval[side]
                if dataval.startswith('[') and dataval.endswith(']'):
                    # artifact
                    data[datakey] = os.path.join(lib_location,
                                                 _mavenname_to_path(dataval[1:-1]))

                elif dataval.startswith('\'') and dataval.endswith('\''):
                    # literal
                    data[datakey] = dataval[1:-1]

                else:
                    self.log.moreinfo('  Extracting: {}'.format(dataval))

                    data_location = os.path.join(lib_location, 'data')
                    if not os.path.exists(data_location):
                        os.makedirs(data_location)

                    installerjar = self._get_installer_jar()
                    with zipfile.ZipFile(installerjar, 'r') as installer:
                        installer.extract(dataval.lstrip('/'), data_location)

                    data[datakey] = os.path.join(data_location, dataval.lstrip('/'))

        manifest = Minecraft(self.minecraft_version).get_version_manifest()

        data['SIDE'] = side
        data['MINECRAFT_JAR'] = os.path.join(lib_location, 'com', 'mojang', 'minecraft',
                                             manifest['id'], 'minecraft-{}-{}.jar'.format(manifest['id'], side))

        self.log.info('Executing forge installer processors ...')
        processors = install_profile['processors']

        i = 0
        for proc in processors:
            i += 1
            self.log.moreinfo('  Running {} of {} processors ...'.format(i, len(processors)))

            classpath = proc['classpath']
            args = proc['args']

            finalargs = []
            for arg in args:
                if arg.startswith('{') and arg.endswith('}'):
                    arg = data[arg[1:-1]]
                elif arg.startswith('[') and arg.endswith(']'):
                    arg = os.path.join(lib_location,
                                       _mavenname_to_path(arg[1:-1]))

                finalargs.append(arg)

            classpath = [os.path.join(lib_location, _mavenname_to_path(proc['jar']))]
            for lib in proc['classpath']:
                classpath.append(os.path.join(lib_location, _mavenname_to_path(lib)))

            mainclass = _find_mainclass_in_jar(os.path.join(lib_location,
                                                            _mavenname_to_path(proc['jar'])))

            cmd = ['java', '-cp', ':'.join(classpath), mainclass]
            cmd.extend(finalargs)

            self.log.debug('cmd = {}'.format(' '.join(cmd)))

            returncode = log_subprocess(self.log.moreinfo, cmd)
            if returncode != 0:
                raise OperationError('Processor finished with errors. Abort')


##############################################################################

FORGE_PROMOTIONS_URL = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/promotions_slim.json"


def calculate_forge_version(minecraft_version, forge_version):
    ver = '{}-{}'.format(minecraft_version, forge_version)
    promos = requests.get(FORGE_PROMOTIONS_URL, timeout=60).json()
    try:
        return promos['promos'][ver]
    except KeyError:
        return None

##############################################################################


def _mavenname_to_path(name):
    parts = name.split(':')
    filename = '{}-{}'.format(parts[2], parts[3]) if len(parts) >= 4 else parts[2]
    filename = filename.replace('@', '.') if '@' in filename else '{}.jar'.format(filename)
    initpath = parts[0].split('.')
    initpath.append(parts[1])
    initpath.append(parts[2].split('@')[0])
    initpath.append('{}-{}'.format(parts[1], filename))
    return '/'.join(initpath)


def _find_mainclass_in_jar(jarfile):
    with zipfile.ZipFile(jarfile, 'r') as jar:
        with jar.open('META-INF/MANIFEST.MF', 'r') as manifest:
            lines = manifest.readlines()
            for line in lines:
                line = line.decode('utf-8').strip()
                if line.startswith('Main-Class:'):
                    return line.split(' ')[1]
    return None

##############################################################################
# THE END
