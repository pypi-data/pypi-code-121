# coding: utf-8
# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from contextlib import contextmanager
import os
from pathlib import Path
from urllib.parse import urlparse

from mercurial import (
    hg,
)

from .ssh import client_command_str

ALLOWED_URL_SCHEMES = ('http', 'https', 'ssh', 'file')


class URLParseError(ValueError):
    """Arguments: (the invalid URL, exception)."""


class InvalidURLScheme(ValueError):
    """Arguments: (the invalid scheme, list of admissible schemes)."""


class FileURLOutsidePath(ValueError):
    """Arguments: incoming URL, allowed path."""


class PeerInitException(RuntimeError):
    """Argument is the underlying exception."""


def init_peer(repo, **kw):
    """Encapsulation of `hg.peer` instantiation with a dedicated exception.


    The dedication exception h with differentiated handling by callers.
    """
    try:
        return hg.peer(repo, **kw)
    except Exception as exc:
        raise PeerInitException(str(exc))


@contextmanager
def hg_remote_peer(repo, peer_description, storage_path,
                   allowed_url_schemes=ALLOWED_URL_SCHEMES):
    """Creation of remote peer from gRPC requests.

    :param peer_description: object having the same attributes as
       the `MercurialPeer` gRPC message

    Because this context manager will be used to create the peer, and then
    to perform some operation on it, the exceptions that can happen on enter
    are catched and reraised as :class:`PeerInitException` so that the
    caller can tell them apart from those raised while using the peer.
    """
    remote_url = peer_description.url
    remote_url_bytes = remote_url.encode('utf-8')
    opts = {}
    try:
        parsed_url = urlparse(remote_url)
    except Exception as exc:
        raise URLParseError(remote_url, exc)

    scheme = parsed_url.scheme or 'file'
    if scheme not in allowed_url_schemes:
        raise InvalidURLScheme(scheme, allowed_url_schemes)

    if scheme == 'file':
        storage_path = os.path.realpath(storage_path)

        # If ever there was HGitaly running on Windows, Pathlib join
        # operator works as one would expect:
        # - the right operand can contain forward slashes,
        #   they get converted to the os separator
        # - a leading forward slash (absolute path of URIs) anchors to
        #   the root of the disk, e.g., `C:\`
        target_path = os.path.realpath(Path(storage_path) / parsed_url.path)
        if not target_path.startswith(storage_path + os.path.sep):
            raise FileURLOutsidePath(remote_url, storage_path)

    if scheme == 'ssh':
        with client_command_str(peer_description.ssh_key,
                                peer_description.ssh_known_hosts) as ssh:
            opts[b'ssh'] = ssh.encode('ascii')
            remote_cmd = peer_description.ssh_remote_command
            if remote_cmd:
                opts[b'remotecmd'] = remote_cmd
            yield init_peer(repo, opts=opts, path=remote_url_bytes)
    else:
        yield init_peer(repo, opts=opts, path=remote_url_bytes)
