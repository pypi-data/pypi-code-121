import asyncio
import datetime
import os
import subprocess

from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

from jija import config
from jija.command import Command


class MultiThreadEvent(asyncio.Event):
    def set(self) -> None:
        self._loop.call_soon_threadsafe(super().set)


class Run(Command):
    def __init__(self):
        super().__init__()
        self.close_event = MultiThreadEvent()
        self.last_reload = datetime.datetime.now()

        self.run_watcher()

    def run_watcher(self):
        event_handler = RegexMatchingEventHandler([r'.*\.py$'])
        event_handler.on_modified = self.modify_callback

        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()

    def modify_callback(self, event):
        if self.reload_timeout() and not self.close_event.is_set():
            self.last_reload = datetime.datetime.now()
            self.close_event.set()

    def reload_timeout(self):
        return datetime.datetime.now() - self.last_reload > datetime.timedelta(seconds=5)

    async def prepare(self):
        pass

    async def handle(self):
        while True:
            runner = subprocess.Popen([config.StructureConfig.PYTHON_PATH, 'main.py', 'runprocess'])
            await self.close_event.wait()
            runner.kill()
            self.close_event.clear()
            print()
