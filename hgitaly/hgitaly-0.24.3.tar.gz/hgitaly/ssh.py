# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
from tempfile import NamedTemporaryFile


@contextmanager
def client_command(priv_key, known_hosts):
    """Context manager providing a suitable ssh client command.

    The command references temporary files that get cleaned up
    automatically when exiting the context.

    :param str priv_key: non-encrypted private key file content.
    """
    with (
            NamedTemporaryFile(mode='w', delete=False) as keyf,
            NamedTemporaryFile(mode='w', delete=False) as known_hostsf,
    ):
        keyf.write(priv_key)
        keyf.close()
        known_hostsf.write(known_hosts)
        known_hostsf.close()

        yield ['ssh',
               '-o', 'IdentitiesOnly=yes',
               '-o', 'UserKnownHostsFile=%s' % known_hostsf.name,
               # do not prompt user if server key is unknown
               '-o', 'StrictHostKeyChecking=yes',
               '-i', keyf.name
               ]


@contextmanager
def client_command_str(*args, **kwargs):
    with client_command(*args, **kwargs) as cmd:
        yield ' '.join(cmd)
