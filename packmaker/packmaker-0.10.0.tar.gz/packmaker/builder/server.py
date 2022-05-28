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

from .base import BaseBuilder
from ..download import HttpDownloader
from ..minecraft import Minecraft, version_as_integer

##############################################################################


class ServerBuilder (BaseBuilder):

    build_subloc = 'server'

    MAVEN_REPOS = ('https://libraries.minecraft.net/',
                   'https://repo1.maven.org/maven2/',
                   'https://files.minecraftforge.net/maven/'
                   )

    temp_server_script = """
#!/bin/sh

MAX_RAM="4096M"

JAVA_PARAMETERS="-XX:+UseG1GC -Dsun.rmi.dgc.server.gcInterval=2147483646"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:+UnlockExperimentalVMOptions"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1NewSizePercent=20"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1ReservePercent=20"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:MaxGCPauseMillis=50"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -XX:G1HeapRegionSize=32M"
JAVA_PARAMETERS="${{JAVA_PARAMETERS}} -Dfml.readTimeout=180"

SERVER_JAR="{}"

echo "Starting minecraft server..."
echo java -server -Xmx${{MAX_RAM}} ${{JAVA_PARAMETERS}} -jar ${{SERVER_JAR}} nogui
exec java -server -Xmx${{MAX_RAM}} ${{JAVA_PARAMETERS}} -jar ${{SERVER_JAR}} nogui
"""

    ##########################################################################

    def setup_build(self, parsed_args):
        super(ServerBuilder, self).setup_build(parsed_args)

        self.mods_location = self.build_location('mods')
        self.libs_location = self.build_location('libraries')

    def do_build(self):
        self.downloader = HttpDownloader(self.cache_location())

        self.log.info('Copying local files ...')
        self.copy_files(files_iterator=self.packlock.yield_serveronly_files())

        self.log.info('Copying mod files ...')
        self.copy_mods(self.mods_location, self.packlock.yield_serveronly_mods())

        mc = Minecraft(self.packlock.get_metadata('minecraft_version'))
        server_jarfile = self.copy_minecraft_server(mc)

        modloader = self.packlock.get_modloader(self.downloader)
        if modloader is not None:
            modloader.install(self.build_location(), 'server')
            jfile = modloader.get_server_jar_filename()
            if jfile is not None:
                server_jarfile = jfile

        self.log.info('Creating stoopid simple launch script (to be replaced soon) ...')
        launch_script = os.path.join(self.build_location(), 'start.sh')
        with open(launch_script, 'w') as startf:
            startf.write(self.temp_server_script.format(server_jarfile))
        os.chmod(launch_script, 0o755)

    ##########################################################################

    def copy_minecraft_server(self, mc):
        mc.download_server(self.downloader.subdownloader('minecraft'))
        manifest = mc.get_version_manifest()

        # Copy the minecraft server library into place.

        cached_lib = os.path.join(self.cache_location('minecraft'), 'versions', manifest['id'], 'server.jar')
        if version_as_integer(self.packlock.get_metadata('minecraft_version')) < 11400:
            local_lib = os.path.join(self.build_location(), 'minecraft_server.{}.jar'.format(manifest['id']))
        else:
            local_lib = os.path.join(self.libs_location, 'com', 'mojang', 'minecraft', manifest['id'],
                                     'minecraft-{}-server.jar'.format(manifest['id']))

        if not os.path.exists(os.path.dirname(local_lib)):
            os.makedirs(os.path.dirname(local_lib))

        shutil.copy2(cached_lib, local_lib)
        server_jarfile = local_lib

        # Copy the minecraft libraries into place.

        for lib in mc.get_libraries():
            cached_lib = os.path.join(self.cache_location('minecraft'), 'libraries', lib.get_path_local())
            if lib.must_extract():
                continue

            localdir = os.path.join(self.libs_location, os.path.dirname(lib.get_path_local()))
            if not os.path.exists(localdir):
                os.makedirs(localdir)

            local_lib = os.path.join(self.libs_location, lib.get_path_local())
            shutil.copy2(cached_lib, local_lib)

        return server_jarfile

##############################################################################
# THE END
