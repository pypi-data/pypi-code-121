# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import time

import pytest

from ..prefork_server import WorkerProcess


def worker_callable(wid, log_path, waiting_time, *args):
    log_path.write("Worker %d starting, remaining args=%r\n" % (wid, args))
    time.sleep(waiting_time)


def ram_eater(wid, log_path, size):
    allocated = list(range(size))
    log_path.write("Worker %d starting, "
                   "allocating a list with %d elements\n" % (wid, size))
    time.sleep(10)
    del allocated


def wait_first_log_line(log_path, timeout=2):
    """Wait for startup to finish by testing log line."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            line = log_path.readlines()[0]
        except Exception:  # pragma no cover
            pass
        else:
            if line.endswith('\n'):
                return line
        time.sleep(timeout / 100)
    return False


@pytest.fixture
def worker_log(tmpdir):
    yield tmpdir / 'worker.log'


def test_process_not_created(worker_log):
    wp = WorkerProcess(process_args=(0, worker_log, 0),
                       process_callable=worker_callable)
    assert str(wp) == "Worker 0 (pid: no process)"

    assert not wp.is_alive()

    # methods that should do nothing and certainly not crash
    wp.join()
    wp.terminate()

    # Caller of monitor is not told to stop (next time, the process is
    # expected to have been created)
    assert wp.watch() is True

    # in that case, a restart just starts the process
    wp.restart()
    assert wp.process is not None
    wp.join()

    assert worker_log.read().strip() == (
        "Worker 0 starting, remaining args=()")


def test_restart(worker_log):
    wp = WorkerProcess.run(process_args=(0, worker_log, 10, 'some_arg'),
                           process_callable=worker_callable)
    line = wait_first_log_line(worker_log)
    first_pid = wp.process.pid
    worker_log.remove()  # for clarity (it would be overwritten anyway)

    wp.restart()
    second_pid = wp.process.pid
    assert second_pid != first_pid
    assert wait_first_log_line(worker_log) == line
    wp.terminate()  # let's not wait for 10 useless seconds
    wp.join()

    assert not wp.is_alive()

    # by default, watch() restarts the process if found not running
    assert wp.watch() is True
    third_pid = wp.process.pid
    assert third_pid != second_pid
    assert wait_first_log_line(worker_log) == line
    wp.terminate()
    wp.join()

    # …but not if the appropriate flag is set
    wp.restart_done_workers = False
    assert wp.watch() is False
    fourth_pid = wp.process.pid
    assert fourth_pid == third_pid
    assert not wp.is_alive()


def test_rss_restart(worker_log):
    # we get 53MiB for the RAM eater with size=10000, almost the same with
    # 100000, hence it's mostly Python's overhead. These figures would
    # trigger the restart but perhaps would be too much context-dependent.
    # We finally get and finally 89Mib with size being one million.
    wp = WorkerProcess.run(process_callable=ram_eater,
                           process_args=(0, worker_log, 1000000),
                           max_rss=10 << 20)
    assert wait_first_log_line(worker_log)
    worker_log.remove()

    pid1 = wp.process.pid
    assert wp.watch() is True
    assert wait_first_log_line(worker_log)
    assert wp.process.pid != pid1

    wp.terminate()
    wp.join()
