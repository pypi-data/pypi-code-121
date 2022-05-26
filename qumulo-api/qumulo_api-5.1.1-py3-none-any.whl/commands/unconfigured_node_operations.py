# Copyright (c) 2013 Qumulo, Inc.
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

import qumulo.lib.opts
import qumulo.rest.unconfigured_node_operations as node_operations

from qumulo.rest_client import RestClient


class ListUnconfiguredNodesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'unconfigured_nodes_list'
    SYNOPSIS = 'Get the list of unconfigured nodes'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--table', action='store_true', help='Print output as a table, instead of JSON'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        res = node_operations.list_unconfigured_nodes(rest_client.conninfo, rest_client.credentials)
        if args.table:
            print(node_operations.fmt_unconfigured_nodes(res))
        else:
            print(res)
