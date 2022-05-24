# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from mercurial import (
    hg,
)

from ..peer import (
    PeerInitException,
    hg_remote_peer,
)

from ..stub.mercurial_repository_pb2 import (
    MercurialPeer,
)


def raiser(msg):
    raise RuntimeError(msg)


def test_peer_context_init_error(monkeypatch):
    """Errors in peer instantiation are properly re-encapsulated"""
    monkeypatch.setattr(hg, 'peer',
                        lambda *a, **kw: raiser('test-peer-init'))
    with pytest.raises(PeerInitException) as exc_info:
        with hg_remote_peer(
                None,
                MercurialPeer(url="http://heptapod.test/valid/url"),
                storage_path='/does/not/matter/here'):
            pass
    assert exc_info.value.args[0] == 'test-peer-init'


def test_peer_context_caller_error(monkeypatch):
    """Errors while using the peer context are not catched.

    Therefore they can be told apart from those in peer initialization
    """
    monkeypatch.setattr(hg, 'peer', lambda *a, **kw: None)

    with pytest.raises(RuntimeError) as exc_info:
        with hg_remote_peer(
                None,
                MercurialPeer(url="http://heptapod.test/valid/url"),
                storage_path='/does/not/matter/here'):
            raise RuntimeError('error-while-using-peer')

    exc = exc_info.value
    assert not isinstance(exc, PeerInitException)
    assert exc_info.value.args[0] == 'error-while-using-peer'
