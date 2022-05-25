import contextlib
import itertools
import logging
import queue
import sys

import click
import click_spinner
import click_threading

_LOGGING = logging.getLogger(__name__)


class WorkerQueue(object):
    '''
    Based on https://github.com/pimutils/vdirsyncer
    A simple worker-queue setup.
    Note that workers quit if queue is empty. That means you have to first put
    things into the queue before spawning the worker!
    '''

    def __init__(self, max_workers):
        self._queue = queue.Queue()
        self._workers = []
        self._max_workers = max_workers
        self._shutdown_handlers = []

        # According to http://stackoverflow.com/a/27062830, those are
        # thread safe compared to increasing a simple integer variable.
        self.num_done_tasks = itertools.count()
        self.num_failed_tasks = itertools.count()

    def shutdown(self):
        while self._shutdown_handlers:
            try:
                self._shutdown_handlers.pop()()
            except Exception:
                pass

    def _worker(self):
        while True:
            try:
                func = self._queue.get(False)
            except queue.Empty:
                break

            try:
                func()
            except Exception as ex:
                _LOGGING.warning(ex)
                next(self.num_failed_tasks)
            finally:
                self._queue.task_done()
                next(self.num_done_tasks)
                if not self._queue.unfinished_tasks:
                    self.shutdown()

    def spawn_worker(self):
        if self._max_workers and len(self._workers) >= self._max_workers:
            return

        t = click_threading.Thread(target=self._worker)
        t.start()
        self._workers.append(t)

    @contextlib.contextmanager
    def join(self, debug=False):
        assert self._workers or not self._queue.unfinished_tasks
        ui_worker = click_threading.UiWorker()
        self._shutdown_handlers.append(ui_worker.shutdown)
        _echo = click.echo
        _secho = click.secho

        with ui_worker.patch_click():
            yield

            if not self._workers:
                # Ugly hack, needed because
                # ui_worker is not running.
                click.echo = _echo
                click.secho = _secho
                _LOGGING.critical('Nothing to do.')
                sys.exit(5)
            with click_spinner.spinner(disable=debug):
                ui_worker.run()
                self._queue.join()
                for worker in self._workers:
                    worker.join()

        tasks_failed = next(self.num_failed_tasks)
        tasks_done = next(self.num_done_tasks)

        if tasks_failed > 0:
            _LOGGING.error(
                '{} out of {} tasks failed.'.format(tasks_failed, tasks_done)
            )
            sys.exit(1)

    def put(self, f):
        return self._queue.put(f)
