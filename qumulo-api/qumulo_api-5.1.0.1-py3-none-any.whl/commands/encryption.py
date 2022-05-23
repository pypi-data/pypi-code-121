# Copyright (c) 2020 Qumulo, Inc.
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
import qumulo.rest.encryption as encryption

from qumulo.rest_client import RestClient


class RotateEncryptionKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 'rotate_encryption_keys'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = encryption.rotate_keys(rest_client.conninfo, rest_client.credentials)
        assert resp.data is None, f'Unexpected response from key rotation API: {resp}'
        print('Key rotation complete')


class EncryptionGetStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_status'
    SYNOPSIS = 'Get at-rest encryption status.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = encryption.status(rest_client.conninfo, rest_client.credentials)
        print(resp)
