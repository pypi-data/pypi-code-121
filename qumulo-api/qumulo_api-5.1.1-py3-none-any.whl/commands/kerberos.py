# Copyright (c) 2018 Qumulo, Inc.
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

import qumulo.lib.util as util
import qumulo.rest.kerberos as kerberos

from qumulo.lib.opts import Subcommand
from qumulo.rest_client import RestClient

#  _              _        _
# | | _____ _   _| |_ __ _| |__
# | |/ / _ \ | | | __/ _` | '_ \
# |   <  __/ |_| | || (_| | |_) |
# |_|\_\___|\__, |\__\__,_|_.__/
#           |___/
#  FIGLET: keytab
#


class KerberosGetKeytab(Subcommand):
    NAME = 'kerberos_get_keytab'
    SYNOPSIS = 'Get the Kerberos keytab'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(kerberos.get_keytab(rest_client.conninfo, rest_client.credentials))


class KerberosSetKeytab(Subcommand):
    NAME = 'kerberos_set_keytab'
    SYNOPSIS = 'Set the Kerberos keytab'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-k',
            '--keytab-file',
            type=argparse.FileType('rb'),
            help='The Kerberos keytab file to set',
            required=True,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(
            kerberos.set_keytab_file(
                rest_client.conninfo, rest_client.credentials, args.keytab_file
            )
        )


class KerberosDeleteKeytab(Subcommand):
    NAME = 'kerberos_delete_keytab'
    SYNOPSIS = 'Delete the Kerberos keytab'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(kerberos.delete_keytab(rest_client.conninfo, rest_client.credentials))


#           _   _   _
#  ___  ___| |_| |_(_)_ __   __ _ ___
# / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/\___|\__|\__|_|_| |_|\__, |___/
#                           |___/
#  FIGLET: settings
#


class KerberosGetSettings(Subcommand):
    NAME = 'kerberos_get_settings'
    SYNOPSIS = 'Get the Kerberos settings'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(kerberos.get_settings(rest_client.conninfo, rest_client.credentials))


class KerberosModifySettings(Subcommand):
    NAME = 'kerberos_modify_settings'
    SYNOPSIS = 'Modify the Kerberos settings'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-a',
            '--use-alt-security-identities-mapping',
            type=util.bool_from_string,
            help=(
                'When enabled, map kerberos-authenticated users to LDAP '
                'records via the altSecurityIdentities field'
            ),
            required=True,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(
            kerberos.modify_settings(
                rest_client.conninfo,
                rest_client.credentials,
                use_alt_security_identities_mapping=args.use_alt_security_identities_mapping,
            )
        )
