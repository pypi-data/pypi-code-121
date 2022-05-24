# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import multiprocessing
import pytest
import signal
import socket
import sys
from socket import (
    AF_INET,
    AF_INET6,
)
import time

from .. import server
from ..prefork_server import WorkerProcess


def test_exceptions():
    storages = dict(default='/some/path')

    # unterminated IPv6 address, one of the very few cases of unparseable URL
    url = 'tcp://[::'
    with pytest.raises(server.InvalidUrl) as exc_info:
        server.init([url], storages)
    assert exc_info.value.args == (url, 'Invalid IPv6 URL')

    # unsupported scheme
    url = 'exotic://localhost:1234'
    with pytest.raises(server.UnsupportedUrlScheme) as exc_info:
        server.init([url], storages)
    assert exc_info.value.args == ('exotic', )

    # bind error
    url = 'tcp://unresolvable-or-youre-kidding-me:0'
    with pytest.raises(server.BindError) as exc_info:
        server.init([url], storages)
    assert exc_info.value.args == (url, )

    # bind error with fixed port
    url = 'tcp://unresolvable-or-youre-kidding-me:1234'
    with pytest.raises(server.BindError) as exc_info:
        server.init([url], storages)
    assert exc_info.value.args == (url, )

    # bind error for non available port
    sock = None
    try:
        sock = socket.socket(socket.AF_INET)
        sock.bind(('127.0.0.1', 0))
        url = 'tcp://%s:%d' % sock.getsockname()
        with pytest.raises(server.BindError) as exc_info:
            server.init([url], storages)
    finally:
        assert sock is not None
        sock.close()
    assert exc_info.value.args == (url, )


def raiser(exc, *exc_args):
    def f(*a, **kw):
        raise exc(*(exc_args or ('something', )))

    return f


def test_catch_netloc_value_error(monkeypatch):

    # errors parsing the netloc
    monkeypatch.setattr(server, 'analyze_netloc', raiser(ValueError))
    url = "tcp://localhost"
    with pytest.raises(server.InvalidUrl) as exc_info:
        with server.prebind_sockets([url]):
            pass
    assert exc_info.value.args == (url, )


def test_so_portreuse_error(monkeypatch):
    monkeypatch.setattr(socket.socket, 'getsockopt', lambda *a: 0)
    url = "tcp://whatever"
    with pytest.raises(server.SocketReusePortError) as exc_info:
        with server.prebind_sockets([url]):
            pass
    assert exc_info.value.args == (url, )


def test_prebind_sockets(monkeypatch):
    bind_records = []

    def fake_bind(sock, port_info):
        bind_records.append(port_info)

    monkeypatch.setattr(socket.socket, 'bind', fake_bind)

    with server.prebind_sockets(['tcp://127.0.0.1:0',
                                 'tcp://[::1]:0',
                                 'tcp://localhost:0',
                                 'unix:/rel/path',
                                 ]):
        pass

    assert bind_records == [('127.0.0.1', 0),
                            ('::1', 0),
                            ('localhost', 0),
                            ]

    # a getsockopt that gives expected success values only for IPv4
    def getsockopt(sock, *a, **kw):
        if a[1] != socket.SO_REUSEPORT:
            return socket.getsockopt(*a, **kw)
        return 0 if sock.family == AF_INET else 1

    monkeypatch.setattr(socket.socket, 'getsockopt', getsockopt)

    del bind_records[:]

    # will fail on the second, hence call the close() for the first
    # that doesn't fail and coverage tells us it's really called
    with pytest.raises(server.SocketReusePortError):
        with server.prebind_sockets(['tcp://127.0.0.1:0',
                                     'tcp://[::1]:0',
                                     ]):
            pass


def test_init_tcp():
    storages = dict(default='/some/path')
    server_instance = server.init(['tcp://localhost:0'], storages)
    try:
        server_instance.start()
    finally:
        server_instance.stop(None)
        server_instance.wait_for_termination()


def test_init_unix(tmpdir):
    storages = dict(default='/some/path')
    # 'unix://PATH' requires PATH to be absolute, whereas 'unix:PATH' does not.
    # currently, str(tmpdir) seems to be always absolute, but let's not depend
    # on that.
    url = 'unix:%s' % tmpdir.join('hgitaly.socket')
    server_instance = server.init([url], storages)
    try:
        server_instance.start()
    finally:
        server_instance.stop(None)
        server_instance.wait_for_termination()


def test_analyze_netloc():
    analyze = server.analyze_netloc

    assert analyze('127.1.2.3') == (AF_INET, '127.1.2.3', None)
    assert analyze('127.1.2.3:66') == (AF_INET, '127.1.2.3', 66)

    for ip6 in ('::1', '2001:db8:cafe::1', '2001:db8:1:2:3:4:5:6'):
        assert analyze('[%s]' % ip6) == (AF_INET6, ip6, None)
        assert analyze('[%s]:66' % ip6) == (AF_INET6, ip6, 66)

    with pytest.raises(ValueError) as exc_info:
        analyze('[::1')
    assert exc_info.value.args == ('[::1', )

    with pytest.raises(ValueError) as exc_info:
        analyze('[::]foo')
    assert exc_info.value.args == ('[::]foo', )


def test_apply_default_port():
    adp = server.apply_default_port
    for host in ('localhost', '[::1]', '127.0.0.1'):
        assert adp(host + ':123') == host + ':123'
        assert adp(host) == host + ':' + str(server.DEFAULT_TCP_PORT)


def test_server_process(tmpdir):
    socket_path = tmpdir.join('hgitaly.socket')
    repos_root = tmpdir.join('repos').ensure(dir=True)
    p = multiprocessing.Process(
        target=server.server_process,
        args=(0, ['unix://' + str(socket_path)],
              dict(default=str(repos_root))))
    p.start()
    p.kill()
    p.join()


def test_run_forever(monkeypatch, tmpdir):

    # server processes are subprocesses. We're only interested into
    # proper start/stop and correct arguments dispatching. Let's have
    # them write that to a file.
    workers_log = tmpdir.join('worker-start.log')

    def fake_server(wid, urls, storages):
        with open(workers_log, 'a') as logf:
            logf.write("%d %s\n" % (wid, ' '.join(urls)))

    def read_workers():
        res = {}
        for line in workers_log.readlines():
            split = line.split()
            wid = int(split[0])
            for url in split[1:]:
                res.setdefault(url, []).append(wid)
        workers_log.remove()
        return res

    monkeypatch.setattr(server, 'server_process', fake_server)

    tcp_url = 'tcp://localhost:1234'
    unix_url = 'unix:/hgitaly.socket'

    server.run_forever([tcp_url], {}, nb_workers=3, mono_process=True)
    workers = read_workers()
    assert sum(len(wids) for wids in workers.values()) == 1

    server.run_forever([tcp_url], {},
                       nb_workers=3,
                       monitoring_interval=0.01)
    workers = read_workers()
    assert len(workers[tcp_url]) == 3

    # we don't want more than one worker per unix URL because it's not
    # implemented yet
    server.run_forever([unix_url], {},
                       nb_workers=5,
                       monitoring_interval=0.01)

    workers = read_workers()
    assert len(workers[unix_url]) == 1

    # mixed scenario
    server.run_forever([unix_url, tcp_url], {},
                       nb_workers=5,
                       monitoring_interval=0.01)
    workers = read_workers()
    assert workers[unix_url] == [0]
    assert set(workers[tcp_url]) == {0, 1, 2, 3, 4}

    # defaulting based on CPU count
    server.run_forever([tcp_url], {}, None,
                       monitoring_interval=0.01)
    assert tcp_url in workers  # not so obvious if there's only one CPU

    # at least 2 unless we are on a single CPU system
    monkeypatch.setattr(multiprocessing, 'cpu_count', lambda: 2)
    assert len(workers[tcp_url]) >= 2


def test_terminate_workers(monkeypatch, tmpdir):

    def worker_callable(wid, queue):
        def bye(*a):
            queue.put((wid, 'bye'))
            sys.exit(0)

        signal.signal(signal.SIGTERM, bye)
        queue.put((wid, 'ready'))
        time.sleep(10)  # should be 100x times enough
        queue.put((wid, 'timeout'))

    queue = multiprocessing.Queue()

    def read_messages():
        msgs = {}
        for _ in range(2):
            msg = queue.get()
            msgs[msg[0]] = msg[1]
        return msgs

    workers = [WorkerProcess(process_args=(wid, queue),
                             process_callable=worker_callable)
               for wid in range(3)]

    for wp in workers:
        wp.init_process()

    # omitting to start a worker to trigger exception in its
    # termination, hence testing that we aren't impaired by that.
    for worker in workers[1:]:
        worker.start()

    # wait for all running workers to be ready to handle signal
    assert read_messages() == {wid: 'ready' for wid in range(1, 3)}

    shutdown_required = server.MutableBoolean(False)
    server.terminate_workers(shutdown_required, workers, signal.SIGTERM)
    for worker in workers[1:]:
        worker.join()

    assert shutdown_required  # flipped by terminate_workers()
    assert read_messages() == {wid: 'bye' for wid in range(1, 3)}


def test_mutable_boolean():
    mut_bool = server.MutableBoolean(False)
    assert bool(mut_bool) is False
    assert not mut_bool

    # demonstrate the main use-case: passing down to any callable
    # and getting back the changed value.
    def mutator(mutable, v):
        mutable.set(v)

    mutator(mut_bool, True)
    assert bool(mut_bool) is True
    assert mut_bool

    # getting back
    mutator(mut_bool, False)
    assert bool(mut_bool) is False
    assert not mut_bool
