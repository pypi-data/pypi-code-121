# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixtures for Gitaly comparison tests.

Some people don't like the ``conftest.py`` magic, and it is true it is
possible to share fixtures amongst test modules by direct imports instead.

But direct imports of fixtures have a severe drawback: if fixture `b` depends
on fixture `a`, then importing `b` is not enough. Implicitely, pytest will
look for `a` where `b` is imported, so that actually both have to be imported,
even if the tests using `b` don't have `a` in their signatures.

This can probably cost developers a few hours of debugging, so not fighting
the framework seems the right thing to do, here.

Another drawback (minor) is that pyflakes doesn't understand that an imported
fixture is actually used leading to these errors::

  from .gitaly import gitaly_channel   # F401 (not used)

  def test_something(gitaly_channel):  # F811 (redefinition of unused import)
      pass

To keep the magic low, we have most of the logic in the `gitaly` and
`comparison` modules.
"""
import pytest
from .gitaly import GitalyServer
from .comparison import gitaly_comparison_fixture


@pytest.fixture(scope='module')
def gitaly_channel(server_repos_root):
    with GitalyServer(server_repos_root).start() as channel:
        yield channel


@pytest.fixture()
def gitaly_comparison(server_repos_root,  # module scope
                      gitaly_channel,  # module scope
                      grpc_channel,  # module scope
                      monkeypatch,  # function scope
                      ):
    with gitaly_comparison_fixture(server_repos_root,
                                   gitaly_channel,
                                   grpc_channel,
                                   monkeypatch,
                                   ) as comparison:
        yield comparison
