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

import qumulo.rest.checksumming as checksumming

from qumulo.lib.opts import Subcommand
from qumulo.rest_client import RestClient


class ChecksummingStatusCommand(Subcommand):
    NAME = 'checksumming_get_status'
    SYNOPSIS = 'Get the checksumming status of the cluster.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(checksumming.get_status(rest_client.conninfo, rest_client.credentials))
