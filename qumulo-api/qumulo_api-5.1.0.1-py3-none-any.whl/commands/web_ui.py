# Copyright (c) 2022 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# qumulo_python_versions = { 3.6, latest }

import argparse

from datetime import timedelta

import qumulo.lib.opts
import qumulo.lib.util as util

from qumulo.rest.web_ui import WebUiSettings
from qumulo.rest_client import RestClient


# Format the Web UI settings to be human-readable
class SettingsForDisplay:
    def __init__(self, settings: WebUiSettings):
        if settings.inactivity_timeout is None:
            self.inactivity_timeout = 'Not set'
        else:
            inactivity_timeout_minutes = int(settings.inactivity_timeout / timedelta(minutes=1))
            self.inactivity_timeout = f'{inactivity_timeout_minutes} minutes'

    def __str__(self) -> str:
        return util.tabulate([['Inactivity timeout:', self.inactivity_timeout]])


class GetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'web_ui_get_settings'
    SYNOPSIS = 'Get configuration options for the Web UI'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        settings = rest_client.web_ui.get_settings()
        display_settings = SettingsForDisplay(settings.data)
        print(display_settings)


class ModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'web_ui_modify_settings'
    SYNOPSIS = 'Modify configuration options for the Web UI'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        timeout_group = parser.add_mutually_exclusive_group(required=True)
        timeout_group.add_argument(
            '--inactivity-timeout',
            help='Sets the inactivity timeout',
            metavar='MINUTES',
            dest='inactivity_timeout',
            type=int,
        )
        timeout_group.add_argument(
            '--disable-inactivity-timeout',
            help='Disables the inactivity timeout',
            action='store_const',
            const=None,
            dest='inactivity_timeout',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.inactivity_timeout is None:
            inactivity_timeout = None
        else:
            inactivity_timeout = timedelta(minutes=int(args.inactivity_timeout))
        rest_client.web_ui.set_settings(WebUiSettings(inactivity_timeout=inactivity_timeout))
