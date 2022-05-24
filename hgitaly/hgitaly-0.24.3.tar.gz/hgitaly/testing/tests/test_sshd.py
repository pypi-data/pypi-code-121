# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from mercurial_testhelpers.repo_wrapper import RepoWrapper
from ..sshd import hg_ssh_setup
from hgitaly.ssh import client_command_str
from hgitaly.testing.ssh import hg_exe_path


@pytest.fixture
def ssh_setup(tmpdir):
    working_dir = tmpdir / 'working'
    working_dir.mkdir()
    yield from hg_ssh_setup(working_dir)


def test_ssh_server(ssh_setup, tmpdir):
    server, client_key, known_hosts = ssh_setup
    src = RepoWrapper.init(tmpdir / 'src')
    dest = RepoWrapper.init(tmpdir / 'dst')
    ctx = src.commit_file('foo')

    with client_command_str(client_key, known_hosts) as ssh_cmd:
        src.command('push',
                    f'ssh://{server.host}:{server.port}/{dest.path}'.encode(),
                    ssh=ssh_cmd.encode(),
                    remotecmd=hg_exe_path().encode(),
                    )
    assert ctx in dest.repo
