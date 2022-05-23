import asyncio
import logging
import signal
import os

logger = logging.getLogger(__name__)

_DEFAULT_DELAY = 0.1

class LoopHelper:

    # TODO: mm - remove kwargs with better readable params
    def __init__(self, loop=asyncio.get_event_loop(), **kwargs):
        self._loop = loop
        self._tasks = []
        self._run_forever = kwargs.get('run_forever', not self._loop.is_running())
        self._install_signals = kwargs.get('install_signals', True)

        self.on_shutdown = kwargs.get('on_shutdown', self.__internal_on_shutdown)

    def create_task(self, task_callback):
        task = asyncio.run_coroutine_threadsafe(task_callback(), self._loop)
        self._tasks.append(task)

    def register_delayed_task(self, task_func, **options):
        logger.info(f"create delayed tasks with options ({options}).")
        task = asyncio.run_coroutine_threadsafe(self.__create_delayed_task(task_func, **options), self._loop)
        self._tasks.append(task)

        return task

    def unregister_delayed_task(self, delayed_task, msg=""):
        return self.__unregister_task(delayed_task, msg)

    async def __create_delayed_task(self, task_func, **options):
        async def _worker(delay):
            try:
                logger.info("sleep for {deplay} ms")
                await asyncio.sleep(delay)

                if asyncio.iscoroutinefunction(task_func):
                    logger.debug("running delayed job (async)")
                    await task_func()
                else:
                    logger.debug("running delayed job (sync)")
                    task_func()

            except asyncio.CancelledError as ce:
                logger.debug(f"Cancel the task {ce}")


        if options.get('delay', None) is not None:
            logger.warning('delay is deprecated, please use delay_in_ms')
            options['delay_in_ms'] = options['delay']

        delay = options.get('delay_in_ms', _DEFAULT_DELAY)
        return await _worker(delay)

    def register_background_task(self, task_func, **options):
        logger.info(f"create background worker with options ({options}).")

        task = asyncio.run_coroutine_threadsafe(self.__create_background_task(task_func, **options), self._loop)
        self._tasks.append(task)

        return task

    def unregister_background_task(self, background_task, msg=""):
        return self.__unregister_task(background_task, msg)

    def __unregister_task(self, task, msg):
        can_unregister = True

        if self._tasks.index(task) >= 0:
            logger.info(f"cancel and unregister task: {msg}")
            self._tasks.remove(task)

            try:
                task.cancel()
                logger.info(f"cancelled task: {msg}")
            except asyncio.CancelledError as ce:
                logger.error(f"__unregister_task: {ce}")
                pass
        else:
            logger.warning("did'nt found task to unregister")
            can_unregister = False

        return can_unregister

    async def __create_background_task(self, task_func, **options):
        async def _task(delay):
            running = True

            while running:
                try:
                    if with_delay:
                        logger.debug(f"background worker delay for {delay}")
                        await asyncio.sleep(delay)

                    if asyncio.iscoroutinefunction(task_func):
                        logger.debug("running background job (async)")
                        await task_func()
                    else:
                        logger.debug("running background job (sync)")
                        task_func()

                except asyncio.CancelledError:
                    running = False
                except Exception as e:
                    logger.error(f"Failed run background job with error {e}")

        if options.get('delay', None) is not None:
            logger.warning('delay is deprecated, please use delay_in_seconds')
            options['delay_in_seconds'] = options['delay']

        delay_in_seconds = options.get('delay_in_seconds', _DEFAULT_DELAY)
        with_delay = True if delay_in_seconds > 0 else False

        return await _task(delay_in_seconds)

    def start(self, **kwargs):
        logger.info(f"Starting event loop {kwargs}.")
        try:
            self._run_forever = kwargs.get('run_forever', self._run_forever)

            if self._install_signals:
                self.__register_shutdown()

            if self._run_forever:
                self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.close()

    def run_forever(self):
        self.start(run_forever=True)

    def stop_all_tasks(self):
        logger.info("Stopping tasks.")
        for task in self._tasks:
            try:
                task.cancel()
            except Exception as e:
                logger.warning(f"Task stopped with exception {e}")

    def stop(self):
        logger.info("Stopping event loop.")
        self.stop_all_tasks()

        if self._run_forever:
            logger.info("close the event loop.")
            self._loop.stop()

    async def __internal_on_shutdown(self):
        logger.debug('only internal on_shutdown called')
        await asyncio.sleep(0)

    def __register_shutdown(self):
        async def shutdown(sig):
            logger.info(f"Received exit signal {sig.name}...")

            await self.on_shutdown()

            self.stop()

        signal_handler = lambda sig: asyncio.create_task(shutdown(sig))

        if self.is_win():
            # See https://docs.python.org/3/library/asyncio-platforms.html#windows
            logger.warning("Cannot register signal handler on windows. To indicate shutdown use the close() method.")
        else:
            signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT)

            for s in signals:
                self._loop.add_signal_handler(s, signal_handler, s)

    def is_win(self):
        return os.name == 'nt'
