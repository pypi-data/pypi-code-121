# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Server startup logic.

While the exposition as a Mercurial extension is certainly convenient for
many reasons, it is best to separate what is specific to the extension context
and what is just generic gRPC server code.
"""
import contextlib
from concurrent import futures
import grpc
import logging
import mercurial
from multiprocessing import cpu_count
import signal
import socket
import time
from urllib.parse import urlparse

from .prefork_server import WorkerProcess
from .service.blob import BlobServicer
from .service.commit import CommitServicer
from .service.ref import RefServicer
from .service.diff import DiffServicer
from .service.mercurial_repository import MercurialRepositoryServicer
from .service.repository import RepositoryServicer
from .service.server import ServerServicer

from .stub.blob_pb2_grpc import add_BlobServiceServicer_to_server
from .stub.commit_pb2_grpc import add_CommitServiceServicer_to_server
from .stub.ref_pb2_grpc import add_RefServiceServicer_to_server
from .stub.diff_pb2_grpc import add_DiffServiceServicer_to_server
from .stub.repository_service_pb2_grpc import (
    add_RepositoryServiceServicer_to_server
)
from .stub.mercurial_repository_pb2_grpc import (
    add_MercurialRepositoryServiceServicer_to_server
)
from .stub.server_pb2_grpc import add_ServerServiceServicer_to_server

logger = logging.getLogger(__name__)


DEFAULT_TCP_PORT = 9237
GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS = 60


class UnsupportedUrlScheme(ValueError):
    pass


class BindError(RuntimeError):
    pass


class SocketReusePortError(RuntimeError):
    """If the socket could not be flagged with SO_REUSEPORT"""


class InvalidUrl(ValueError):
    pass


def init(listen_urls, storages):
    """Return server object for given parameters"""

    server_opts = (
        ('grpc.so_reuseport', 1),
        # As of GitLab 14.8.2, this matches the setting used by Rails'
        # Gitlab::GitalyClient.channel_args, hence avoiding the infamous
        # "Too many pings" error. For explanations, see
        # https://github.com/grpc/grpc/blob/master/doc/keepalive.md
        # in which the PARAMETERS_IN_CAPS are apparently to be replaced by the
        # corresponding *values* from https://github.com...
        # .../grpc/grpc/blob/v1.42.x/include/grpc/impl/codegen/grpc_types.h
        ('grpc.http2.min_ping_interval_without_data_ms', 19000),
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1),
                         options=server_opts)
    add_BlobServiceServicer_to_server(BlobServicer(storages), server)
    add_CommitServiceServicer_to_server(CommitServicer(storages), server)
    add_RefServiceServicer_to_server(RefServicer(storages), server)
    add_DiffServiceServicer_to_server(DiffServicer(storages), server)
    add_MercurialRepositoryServiceServicer_to_server(
        MercurialRepositoryServicer(storages), server)
    add_RepositoryServiceServicer_to_server(
        RepositoryServicer(storages), server)
    add_ServerServiceServicer_to_server(ServerServicer(storages), server)

    for url in listen_urls:
        try:
            parsed_url = urlparse(url)
        except ValueError as exc:
            raise InvalidUrl(url, *exc.args)
        try:
            if parsed_url.scheme == 'tcp':
                server.add_insecure_port(apply_default_port(parsed_url.netloc))
            elif parsed_url.scheme == 'unix':
                server.add_insecure_port(url)
            else:
                raise UnsupportedUrlScheme(parsed_url.scheme)
        except RuntimeError:
            raise BindError(url)

    return server


# excluding from coverage, but actually executed in the tests, yet
# in a subprocess, so that we termination (kill) happens. We don't
# have the setup to cover subprocesses (yet).
def server_process(worker_id, listen_urls, storages):  # pragma no cover
    server = init(listen_urls, storages)
    server.start()
    signal.signal(signal.SIGTERM,
                  lambda *a: server.stop(GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS))

    logger.info("Server %d started", worker_id)
    try:
        server.wait_for_termination()
    except mercurial.error.SignalInterrupt:
        # here it would be better to catch the Mercurial signal
        # in our servicer layers and raise the clean thing that
        # grpc probably expects.
        # Another possibility would be to have our own handler in
        # the worker process, but that would perhaps prevent Mercurial
        # from doing its own cleaning.
        logger.info("Terminating on explicit signal")


def analyze_netloc(netloc):
    """Everything needed to bind a TCP socket from a parsed URL

    :return: family, host, port. port is ``None`` if the netloc does not
       specify it.
    """
    if netloc.startswith('['):
        h_end = netloc.find(']')
        if h_end < 0:
            raise ValueError(netloc)
        host = netloc[1:h_end]
        family = socket.AF_INET6

        if h_end + 1 == len(netloc):
            return family, host, None

        if netloc[h_end + 1] != ':':
            raise ValueError(netloc)
        return family, host, int(netloc[h_end + 2:])

    split = netloc.rsplit(':', 1)
    if len(split) == 1:
        host, port = netloc, None
    else:
        host, port = split
        port = int(port)

    # here actually I should let gai do the job
    # the thing is, we *must* do the same
    # as gRPC and I don't know yet what this is
    family = socket.AF_INET
    return family, host, port


def apply_default_port(netloc):
    """Return a netloc with default port applied if port wasn't specified."""
    family, host, port = analyze_netloc(netloc)
    if port is None:
        port = DEFAULT_TCP_PORT
    if family == socket.AF_INET6:
        return '[%s]:%d' % (host, port)
    return '%s:%d' % (host, port)


def prefork_info_from_url(url):
    """Return needed information for prefork processing from URL."""
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise InvalidUrl(url, *exc.args)

    scheme = parsed.scheme
    if scheme in ('tcp', 'tls'):
        try:
            family, host, port = analyze_netloc(parsed.netloc)
        except ValueError:
            # can't really happen after urlparse (does already same checks)
            # still catching to be refactor-proof
            raise InvalidUrl(url)

        if port is None:
            port = DEFAULT_TCP_PORT
        return scheme, (family, host, port)
    else:
        return scheme, None


@contextlib.contextmanager
def prebind_sockets(listen_urls):
    """Pre-bind all sockets with the SO_REUSEPORT option."""
    # failing early if there's one invalid URL in the mix, so that
    # we don't have anything to clean up (this would raise ValueError)
    extracted_urls = ((url, prefork_info_from_url(url)) for url in listen_urls)
    prebound_urls = []

    sockets = []

    def close_sockets():
        for sock in sockets:
            sock.close()

    for url, (scheme, info) in extracted_urls:
        try:
            if scheme == 'tcp':
                family, host, port = info

                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                if sock.getsockopt(socket.SOL_SOCKET,
                                   socket.SO_REUSEPORT) == 0:
                    raise SocketReusePortError(url)
                try:
                    sock.bind((host, port))
                except Exception:
                    logger.exception("Could not bind on %r (bind info=%r)",
                                     url, info)
                    raise BindError(url)
                else:
                    sockets.append(sock)

                info = ("Pre-bound %r for %r", info[1:], url)
                prebound_urls.append(url)
            elif scheme == 'unix':
                info = ("Unix Domain Socket doesn't need port pre-binding", )
            else:
                raise UnsupportedUrlScheme(scheme)

            logger.info(*info)

        except Exception:
            logger.info("Closing previously bound sockets after exception")
            close_sockets()
            raise

    try:
        yield prebound_urls
    finally:
        close_sockets()


def terminate_workers(witness, workers, sig, *a):
    witness.set(True)
    logger.info("Catched signal %d, workers=%r", sig, workers)
    for worker in workers:
        logger.info("Terminating %s (alive is %r)", worker, worker.is_alive())
        # using is_alive() could be subject to a race, whereas
        # terminate() will send SIGTERM as soon as possible.
        try:
            worker.terminate()
        except Exception as exc:
            # only warning because it may not even be alive.
            logger.exception("Terminating worker %s failed: %r",
                             worker, exc)


class MutableBoolean:
    def __init__(self, v):
        self.set(v)

    def set(self, v):
        self.v = v

    def __bool__(self):
        return self.v


def termination_signals(workers, termination):
    """Signal handler for termination.

    :param workers: iterable of the :class:`Process` instances of the workers.
    :param termination: :class:`MutableBoolean` instance that will be set
       to ``True`` to indicate that worker termination is due to this handler.
       Main use-case would be to avoid restarting them.
    """
    for sig_name in ('SIGTERM', 'SIGINT'):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            signal.signal(sig, lambda *a: terminate_workers(
                termination, workers, *a))


def run_forever(listen_urls, storages,
                nb_workers=None,
                restart_done_workers=False,
                monitoring_interval=60,
                max_rss_mib=1024,
                mono_process=False):
    """Run the server, never stopping

    :param listen_urls: list of URLs, given as in the same form as in
       GitLab configuration files.
    :param storages: a :class:`dict`, mapping storage names to the
       corresponding root directories for repositories.
    :param float monitoring_interval: time, in seconds, between successive
       monitorings of workers.
    :param max_rss_mib: maximum Resident Set Size of workers, in MiB. If
       a worker goes over it, it will be gracefully restarted.
    """
    if mono_process:
        return server_process(0, listen_urls, storages)

    if nb_workers is None:
        nb_workers = cpu_count() // 2 + 1

    worker_kwargs = dict(restart_done_workers=restart_done_workers,
                         max_rss=max_rss_mib << 20,
                         )

    with prebind_sockets(listen_urls) as prebound_urls:
        workers = [WorkerProcess.run(process_callable=server_process,
                                     process_args=(0, listen_urls, storages),
                                     **worker_kwargs)]
        if prebound_urls:
            workers.extend(
                WorkerProcess.run(process_callable=server_process,
                                  process_args=(i, prebound_urls, storages),
                                  **worker_kwargs)
                for i in range(1, nb_workers))
        else:
            logger.info("No socket prebound for multiprocessing "
                        "(expected if listening only to Unix Domain socket) "
                        "Starting only one worker")

        general_shutdown = MutableBoolean(False)
        termination_signals(workers, general_shutdown)

        logger.info("All %d worker processes started", len(workers))

        keep_monitoring = True
        while keep_monitoring and not general_shutdown:
            for worker in workers:
                keep_monitoring &= worker.watch()
            time.sleep(monitoring_interval)

        logger.warning("General shutdown required, wrapping up")
        for worker in workers:
            worker.join()
        logger.info("All worker processes are finished. Closing down")
