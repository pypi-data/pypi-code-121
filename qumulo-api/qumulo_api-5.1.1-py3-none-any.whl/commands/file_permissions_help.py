# Copyright (c) 2019 Qumulo, Inc.
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
import sys

from typing import IO

import qumulo.lib.opts

from qumulo.commands.fs import API_RIGHTS_TO_CLI, RIGHT_EXPLANATIONS, SHORTHAND_RIGHTS_TO_API
from qumulo.lib.util import TextAligner

SYNOPSIS = [
    'The QQ CLI includes tools for setting, getting, and understanding file',
    'permissions.',
    '',
]

SHORTHAND_INFO = [
    'QQ tools that describe and interact with permissions will use the',
    'following shorthand for access rights:',
]

PRETTY_RIGHT_EXPLANATIONS = sorted((API_RIGHTS_TO_CLI[k], v) for k, v in RIGHT_EXPLANATIONS.items())

PRETTY_RIGHTS_TABLE = sorted(
    (key, sorted(API_RIGHTS_TO_CLI[v] for v in values))
    for key, values in SHORTHAND_RIGHTS_TO_API.items()
)

RELATED_COMMANDS = sorted(
    [
        'fs_acl_explain_chmod',
        'fs_acl_explain_posix_mode',
        'fs_acl_explain_rights',
        'fs_get_acl',
        'fs_get_permissions_settings',
        'fs_modify_acl',
        'fs_set_acl',
        'fs_set_permissions_settings',
    ]
)


def _print_file_perms_help(outfile: IO[str]) -> None:
    outfile.write('File Permissions\n\n')
    fp_help = TextAligner()
    with fp_help.indented():
        fp_help.add_line('SYNOPSIS')
        with fp_help.indented():
            fp_help.add_lines(lines=SYNOPSIS)
            fp_help.add_line('The following file access rights are supported:')
            with fp_help.indented():
                fp_help.add_wrapped_table(PRETTY_RIGHT_EXPLANATIONS)
                fp_help.add_line('')
            fp_help.add_lines(SHORTHAND_INFO)
            with fp_help.indented():
                fp_help.add_wrapped_table(PRETTY_RIGHTS_TABLE)
        fp_help.add_line('')
        fp_help.add_line('RELATED QQ COMMANDS')
        with fp_help.indented():
            fp_help.add_concatenated_lines(RELATED_COMMANDS)

    fp_help.write(outfile)


class FilePermissionsHelpCommand(qumulo.lib.opts.HelpCommand):
    NAME = 'file_permissions'
    SYNOPSIS = 'Information about Qumulo file permissions'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.set_defaults(function=_print_file_perms_help)

    @staticmethod
    def main(args: argparse.Namespace, outfile: IO[str] = sys.stdout) -> None:
        args.function(outfile)
