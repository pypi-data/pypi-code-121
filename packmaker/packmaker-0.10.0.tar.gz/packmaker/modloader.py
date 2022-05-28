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
import shutil

from .framew.application import ApplicationError, OperationError
from .download import DownloadError
from .framew.log import getlog

##############################################################################


class ModLoader (object):

    def __init__(self, minecraft_version, loader_version, downloader):
        super(ModLoader, self).__init__()
        self.minecraft_version = minecraft_version
        self.loader_version = loader_version
        self.downloader = downloader
        self.log = getlog()

    ##########################################################################

    def get_mainclass(self):
        raise ApplicationError('get_mainclass() called base ModLoader class')

    ##########################################################################

    def get_launch_arguments(self):
        raise ApplicationError('get_launch_arguments() called base ModLoader class')

    ##########################################################################

    def get_libraries(self, side=None):
        raise ApplicationError('get_libraries() called base ModLoader class')

    ##########################################################################

    def install(self, install_location, side):
        raise ApplicationError('install() called base ModLoader class')

    ##########################################################################

    def get_server_jar_filename(self):
        raise ApplicationError('get_server_jar_filename() called base ModLoader class')

    ##########################################################################

    def _install_libraries(self, lib_location, libraries):

        def copy_library(url, filename):
            barepath = filename[len(self.downloader.download_dir):]
            local_library = os.path.join(lib_location, *barepath.split('/'))
            if not os.path.exists(os.path.dirname(local_library)):
                os.makedirs(os.path.dirname(local_library))
            shutil.copy2(filename, local_library)

        for library in libraries:
            self.downloader.add_download(library.get_download_urls, library.get_path())
        try:
            self.downloader.run(post=copy_library)
        except DownloadError:
            raise OperationError('Cannot download library: {}'.format(library.get_filename()))

##############################################################################
# THE END
