"""Support session with Muffin framework."""

import asyncio
import signal
import typing as t

from muffin import Application
from muffin.plugins import BasePlugin

from donald import Donald

__version__ = "0.5.1"
__project__ = "muffin-donald"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


T = t.TypeVar("T", bound=t.Callable)


class Plugin(BasePlugin):

    """Run periodic tasks."""

    # Can be customized on setup
    name = "tasks"
    defaults: t.Dict = {
        "autostart": True,
        "fake_mode": Donald.defaults["fake_mode"],
        "num_workers": Donald.defaults["num_workers"],
        "max_tasks_per_worker": Donald.defaults["max_tasks_per_worker"],
        #  "workers_lifespan": False,
        "filelock": Donald.defaults["filelock"],
        "loglevel": Donald.defaults["loglevel"],
        "queue": False,
        "queue_name": "tasks",
        "queue_params": {},
    }

    donald: Donald = None
    __exc_handler: t.Optional[t.Callable] = None

    def __init__(self, *args, **kwargs):
        """Initialize the plugin."""
        self.donald: Donald = None
        super(Plugin, self).__init__(*args, **kwargs)

    def setup(self, app: Application, **options):
        """Setup Donald tasks manager."""
        super().setup(app, **options)

        sentry = app.plugins.get("sentry")

        self.donald = Donald(
            fake_mode=self.cfg.fake_mode,
            filelock=self.cfg.filelock,
            loglevel=self.cfg.loglevel,
            num_workers=self.cfg.num_workers,
            queue_name=self.cfg.queue_name,
            queue_params=self.cfg.queue_params,
            sentry=sentry
            and sentry.cfg.dsn
            and dict(sentry.cfg.sdk_options, dsn=sentry.cfg.dsn),
        )
        if self.__exc_handler:
            self.donald.on_exception(self.__exc_handler)

        async def tasks_manager(timer: int = 60):
            """Run tasks workers.
            :param timer: Sleep timer for scheduled tasks.
            """
            await self.run(timer)

        app.manage(tasks_manager)

    def __getattr__(self, name):
        """Proxy attributes to the tasks manager."""
        return getattr(self.donald, name)

    async def startup(self):
        """Startup self tasks manager."""
        if self.cfg.autostart:
            await self.start()

        elif self.cfg.queue:
            donald = t.cast(Donald, self.donald)
            await donald.queue.connect()

    async def shutdown(self):
        """Shutdown self tasks manager."""
        donald = t.cast(Donald, self.donald)
        await donald.stop()
        if donald.queue:
            await donald.queue.stop()

    def on_error(self, fn: T) -> T:
        """Register an error handler."""
        self.__exc_handler = fn
        return fn

    def submit(self, task: t.Callable, *args, **kwargs):
        """Submit a task to donald."""
        if self.cfg.queue:
            return self.donald.queue.submit(task, *args, **kwargs)

        return self.donald.submit(task, *args, **kwargs)

    def submit_nowait(self, task: t.Callable, *args, **kwargs):
        """Submit a task to donald."""
        if self.cfg.queue:
            self.donald.queue.submit(task, *args, **kwargs)

        self.donald.submit_nowait(task, *args, **kwargs)

    async def start(self):
        """Start donald."""
        donald = t.cast(Donald, self.donald)
        #  if self.cfg.workers_lifespan:
        #      donald.on_start(self.app.lifespan.run, 'startup')
        #      donald.on_stop(self.app.lifespan.run, 'shutdown')

        started = await donald.start()
        if self.cfg.queue:
            await donald.queue.connect()
            if started:
                await donald.queue.start()
        return started

    async def run(self, timer: int = 60):
        """Run tasks manager continiously."""
        loop = asyncio.get_event_loop()

        if await self.start():
            donald = t.cast(Donald, self.donald)
            runner = asyncio.create_task(donald.run(timer))

            async def stop():
                await self.shutdown()
                runner.cancel()

            loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(stop()))
            loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(stop()))

            try:
                await runner
            except asyncio.CancelledError:
                pass
