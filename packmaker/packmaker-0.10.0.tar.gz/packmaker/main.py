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

from .framew.cmdapplication import CommandApplication
from .cmd import commands

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('packmaker').version
except Exception:
    __version__ = 'unknown'

##############################################################################


class PackmakerMain (CommandApplication):
    app_name = 'packmaker'
    app_version = __version__
    subcommands = commands
    censored_config_params = ['curseforge::authentication_token']

##############################################################################


def main():
    app = PackmakerMain()
    return app.start()


if __name__ == "__main__":
    main()

##############################################################################
# THE END
