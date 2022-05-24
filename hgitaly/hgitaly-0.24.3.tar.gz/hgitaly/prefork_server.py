# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import logging
import psutil
from multiprocessing import Process

logger = logging.getLogger(__name__)


@attr.s
class WorkerProcess:
    """Wrapping a :class:`Process` instance with more utilities."""

    process_callable = attr.ib()
    """The Python callable to run in the process."""

    process_args = attr.ib()
    """The arguments to pass to the underlying Python callable."""

    process = attr.ib(default=None)
    """The :class:`Process` instance."""

    monitoring = attr.ib(default=None)
    """The :class:`psutil.Process` used for monitoring."""

    restart_done_workers = attr.ib(default=True)
    """Control whether :meth:`watch` should restart done workers.

    Not restarting workers is important for tests, where we have short lived
    workers.
    """

    max_rss = attr.ib(default=1 << 30)
    """Maximum memory Resident Set Size before :meth:`watch` restarts.

    Default is 1GiB.
    """

    @classmethod
    def run(cls, *a, **kw):
        wp = cls(*a, **kw)
        wp.init_process()
        wp.start()
        return wp

    def __str__(self):
        pid = 'no process' if self.process is None else self.process.pid
        return f"Worker {self.process_args[0]} (pid: {pid})"

    def init_process(self):
        self.process = Process(target=self.process_callable,
                               args=self.process_args)

    def start(self):
        self.process.start()
        self.monitoring = psutil.Process(self.process.pid)

    def join(self):
        if self.process is not None:
            self.process.join()

    def is_alive(self):
        return False if self.process is None else self.process.is_alive()

    def terminate(self):
        if self.process is not None:
            self.process.terminate()

    def restart(self):
        logger.info("Restarting %s", self)
        self.terminate()
        self.join()
        self.init_process()
        self.start()

    def watch(self):
        """Checks process statistics and restart it if needed.

        :return: ``True`` if monitoring should go on, ``False``
           otherwise.
        """
        if self.monitoring is None:
            logger.debug("%s process not started", self)
            return True

        try:
            restart_or_reap = self.monitoring.status() == 'zombie'
            mem_stats = self.monitoring.memory_info()
        except psutil.NoSuchProcess as exc:
            logger.warning("%s %s", self, exc)
            restart_or_reap = True

        if restart_or_reap:
            if self.restart_done_workers:
                self.restart()
                return True
            self.join()
            return False

        rss = mem_stats.rss
        over_limit_restart = rss > self.max_rss

        log = logger.warning if over_limit_restart else logger.info
        log("%s %sRSS=%dMiB. Full mem stats: %r",
            self, "over limit, will restart: " if over_limit_restart else '',
            rss >> 20, mem_stats)
        if over_limit_restart:
            self.restart()
        return True
