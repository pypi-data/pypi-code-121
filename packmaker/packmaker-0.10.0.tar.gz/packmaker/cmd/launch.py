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
import platform

from .build import BuildLocal
from ..framew.log import getlog, log_subprocess
from ..minecraft import Minecraft

##############################################################################


class LaunchCommand (BuildLocal):
    """
    Launch a local installation
    """
    name = 'launch'

    default_java_binary = 'java'
    default_java_memory = '4096m'
    default_java_arguments = '-XX:+UseG1GC ' \
                             '-XX:+UnlockExperimentalVMOptions ' \
                             '-XX:G1NewSizePercent=20 ' \
                             '-XX:G1ReservePercent=20 ' \
                             '-XX:MaxGCPauseMillis=50 ' \
                             '-XX:G1HeapRegionSize=32M ' \
                             '-Dsun.rmi.dgc.server.gcInterval=2147483646 ' \
                             '-Dfml.readTimeout=180'

    def setup(self):
        super(LaunchCommand, self).setup()
        self.setup_java_arguments()
        self.log = getlog()

    def setup_java_arguments(self):
        self.java_binary = self.config.get('launch::java_binary', self.default_java_binary)
        self.java_memory = self.config.get('launch::java_memory', self.default_java_memory)
        self.java_arguments = self.config.get('launch::java_arguments', self.default_java_arguments)

    def run_command(self, parsed_args):
        super(LaunchCommand, self).run_command(parsed_args)
        self.run_launcher()

    def run_launcher(self):
        mc = Minecraft(self.builder.packlock.get_metadata('minecraft_version'))
        launch_args = mc.get_launch_arguments()
        main_class = mc.get_mainclass()

        loader = self.builder.packlock.get_modloader(self.builder.downloader)
        if loader is not None:
            loader_launch_args = loader.get_launch_arguments()
            if loader_launch_args is not None:
                if loader_launch_args.startswith('--username ${auth_player_name}'):
                    launch_args = loader_launch_args
                else:
                    launch_args = '{} {}'.format(launch_args, loader_launch_args)

            main_class = loader.get_mainclass()

        manifest = mc.get_version_manifest()

        classpath = [os.path.join('libraries', 'com', 'mojang', 'minecraft', manifest['id'],
                                  'minecraft-{}-client.jar'.format(manifest['id']))]

        libraries = {}

        for library in mc.get_libraries():
            if library.must_extract():
                continue
            libraries[library.get_artifact()] = os.path.join('libraries', library.get_path_local())

        if loader is not None:
            for library in loader.get_libraries():
                libraries[library.get_artifact()] = os.path.join('libraries', library.get_path_local())

        classpath.extend(libraries.values())
        if platform.system() == 'Windows':
            classpath = ';'.join(classpath)
        else:
            classpath = ':'.join(classpath)

        launch_args = launch_args.replace('${auth_player_name}', 'Player')
        launch_args = launch_args.replace('${version_name}', manifest['id'])
        launch_args = launch_args.replace('${game_directory}', '.')
        launch_args = launch_args.replace('${assets_root}', 'assets')
        launch_args = launch_args.replace('${assets_index_name}', manifest['assets'])
        launch_args = launch_args.replace('${auth_uuid}', '00000000-0000-0000-0000-000000000000')
        launch_args = launch_args.replace('${auth_access_token}', '0')
        launch_args = launch_args.replace('${user_type}', 'mojang')
        launch_args = launch_args.replace('${user_properties}', '{}')
        launch_args = launch_args.replace('${version_type}', manifest['type'])

        cmdline = ' '.join([self.java_binary, '-cp', classpath,
                            '-Xms{}'.format(self.java_memory), '-Xmx{}'.format(self.java_memory),
                            self.java_arguments,
                            '-Djava.library.path={}'.format('natives'),
                            main_class, launch_args])

        self.log.info('Launching minecraft process...')
        self.log.debug('cmd = {}'.format(cmdline))

        result = log_subprocess(self.log.info, cmdline, cwd=self.builder.build_location(), shell=True)
        if result != 0:
            self.log.warn('Minecraft process exited with an error.')

##############################################################################
# THE END
