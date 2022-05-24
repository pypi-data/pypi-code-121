# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import pytest

from mercurial import (
    error,
)
from heptapod.testhelpers import (
    make_ui,
    LocalRepoWrapper,
)

import hgext3rd.hgitaly as hgitaly_ext
HGEXT_HGITALY_SOURCE = os.path.dirname(hgitaly_ext.__file__)

DEFAULT_LISTEN_URL_STR = hgitaly_ext.DEFAULT_LISTEN_URL.decode()


def activating_config():
    return dict(extensions=dict(hgitaly=HGEXT_HGITALY_SOURCE))


def recorder(recorders):
    def inner(*args, **kwargs):
        recorders.append((args, kwargs))

    return inner


def mock_run_forever(tmpdir, monkeypatch, config=None):
    """Uses the monkeypatch fixture to mock `hgitaly.server.run_forever`

    :return: ``ui, records`` where ``records`` is a list that will receive
       a pair `(args, kwargs)` for each call of the  mocked `run_forever`
    """
    # using RepoWrapper is pure lazyness on our part: they  give us the easiest
    # access to fully set up `ui` objects, with activated extensions
    if config is not None:
        # simple merge logic
        for section, items in config.items():
            config.setdefault(section, {}).update(items)
    ui = LocalRepoWrapper.init(tmpdir, config=config).repo.ui
    records = []
    monkeypatch.setattr(hgitaly_ext, 'run_forever', recorder(records))
    return ui, records


def test_serve_default_url(tmpdir, monkeypatch):
    ui, records = mock_run_forever(tmpdir, monkeypatch)
    hgitaly_ext.serve(ui, listen=[], repositories_root=b'/some/path')
    (listen_urls, storages), kwargs = records[0]

    # we have no bytes in the inner call
    assert listen_urls == [DEFAULT_LISTEN_URL_STR]
    assert storages == dict(default=b'/some/path')

    # default for workers is also expected to be ``None``
    # (be it explicitely passed or not)
    assert kwargs.get('nb_workers') is None


def test_serve_workers_config(tmpdir, monkeypatch):
    ui, records = mock_run_forever(tmpdir, monkeypatch,
                                   config=dict(hgitaly=dict(workers='47')))
    hgitaly_ext.serve(ui, listen=[], repositories_root=b'/some/path')
    kwargs = records[0][1]
    assert kwargs.get('nb_workers') == 47


def test_serve_max_rss_mb(tmpdir, monkeypatch):
    ui, records = mock_run_forever(
        tmpdir, monkeypatch,
        config=dict(hgitaly={'worker.max-rss-mib': '128'}))
    hgitaly_ext.serve(ui, listen=[], repositories_root=b'/some/path')
    kwargs = records[0][1]
    assert kwargs.get('max_rss_mib') == 128


def test_serve_monitoring_interval(tmpdir, monkeypatch):
    ui, records = mock_run_forever(
        tmpdir, monkeypatch,
        config=dict(hgitaly={'worker.monitoring-interval-seconds': '13'}))
    hgitaly_ext.serve(ui, listen=[], repositories_root=b'/some/path')
    kwargs = records[0][1]
    assert kwargs.get('monitoring_interval') == 13


def test_serve_config_repositories_root(tmpdir, monkeypatch):
    ui, records = mock_run_forever(tmpdir, monkeypatch)
    ui.setconfig(b'heptapod', b'repositories-root', b'/explicit/path')
    hgitaly_ext.serve(ui, listen=[])
    listen_urls, storages = records[0][0]

    # we have no bytes in the inner call
    assert listen_urls == [DEFAULT_LISTEN_URL_STR]
    assert storages == dict(default=b'/explicit/path')


def test_missing_repos_root():
    ui = make_ui(None, config=activating_config())
    with pytest.raises(error.Abort) as exc_info:
        hgitaly_ext.serve(ui, listen=[])
    assert b'repositories-root' in exc_info.value.args[0]


def test_reraising():
    # the point here is that we don't mock run_forever() , instead
    # we test the whole loop from bad arguments, leading hgitaly.server.init()
    # to raise exceptions and we test the final conversions of the latter.
    ui = make_ui(None, config=activating_config())
    repos_root = b'/some/path'

    invalid_ipv6_url = b'tcp://[::'
    with pytest.raises(error.Abort) as exc_info:
        hgitaly_ext.serve(ui, listen=[invalid_ipv6_url],
                          repositories_root=repos_root)
    message = exc_info.value.args[0]
    assert invalid_ipv6_url in message
    assert b'Invalid IPv6 URL' in message  # explanation from urlparse()

    unsupported_scheme_url = b'exotic://localhost:1234'
    with pytest.raises(error.Abort) as exc_info:
        hgitaly_ext.serve(ui, listen=[unsupported_scheme_url],
                          repositories_root=repos_root)
    message = exc_info.value.args[0]
    assert b"scheme: 'exotic'" in message

    cant_bind_url = b'tcp://unresolvable-or-youre-kidding-me:1234'
    with pytest.raises(error.Abort) as exc_info:
        hgitaly_ext.serve(ui, listen=[cant_bind_url],
                          repositories_root=repos_root)
    message = exc_info.value.args[0]
    assert cant_bind_url in message
    assert b'could not listen' in message
