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

__all__ = ['commands']

from .apidebug import ApidebugCommand
from .build import BuildCurseforge, BuildLocal, BuildPack, BuildServer, BuildRouthio
from .convert import ConvertCommand
from .findupdates import FindUpdatesCommand
from .info import InfoCommand
from .launch import LaunchCommand
from .lock import LockCommand
from .modsinfo import ModsInfoCommand
from .resourcepacksinfo import ResourcepacksInfoCommand
from .search import SearchCommand
from .updatedb import UpdateDbCommand

##############################################################################

commands = [
             ApidebugCommand,
             BuildCurseforge,
             BuildLocal,
             BuildPack,
             BuildRouthio,
             BuildServer,
             ConvertCommand,
             FindUpdatesCommand,
             InfoCommand,
             LaunchCommand,
             LockCommand,
             ModsInfoCommand,
             ResourcepacksInfoCommand,
             SearchCommand,
             UpdateDbCommand,
           ]

##############################################################################
# THE END
