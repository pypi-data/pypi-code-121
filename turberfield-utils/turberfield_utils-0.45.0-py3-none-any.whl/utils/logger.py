#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

"""
.. code-block:: python

    from turberfield.utils.logger import LogManager

    logger = LogManager().get_logger("root")
    logger.info("Hello, World!")

.. code-block:: shell

    2022-05-25 18:40:00.766978|    INFO|root| Hello, World!

The main feature of these Loggers is that you can set them to format any
arbitrary data you might want to send them.

A logger has a frame which is a list of the formats of all the fields
it can present to a LogAdapter.

.. code-block:: python

    print(logger.frame)

.. code-block:: shell

    ['{now}', '{level.name:>8}', '{logger.name}', ' {0}']

This frame can be modified at run time to add extra fields to the log.
Unlike the standard logging module, it doesn't matter if that data is missing:

.. code-block:: python

    import http

    logger.frame += ["{status.name}"]
    logger.info("Situation report", status=http.HTTPStatus.OK)

.. code-block:: shell

    2022-05-25 18:53:51.767937|    INFO|root| Situation report|OK

You can supply a customised LogAdapter to perform filtering or reformatting
on an endpoint-specific basis.

.. code-block:: python

    import re
    import platform

    from turberfield.utils.logger import LogAdapter

    class Alarmist(LogAdapter):

        patterns = [
            (re.compile("NOTE"), (234, 0, 255)),
            (re.compile("INFO"), (0, 255, 255)),
            (re.compile("ERROR"), (234, 255, 0)),
            (re.compile("WARNING"), (255, 106, 0)),
            (re.compile("CRITICAL"), (255, 0, 106)),
        ]

        def colour_field(self, field, word):
            if "level" in field:
                r, g, b = next(
                    (c for r, c in self.patterns if r.search(word)),
                    (200, 200, 200)
                )
                return f"\033[38;2;{r};{g};{b}m{word}\033[0m"
            else:
                return word

        def render(self, entry):
            if platform.system().lower() == "windows":
                return super().render(entry)

            return "|".join(
                self.colour_field(f, w)
                for f, w in zip(entry.origin.frame, entry.tokens)
            )

Once you have configured a logger, you can clone it as the basis of another.

.. code-block:: python

    root_logger = log_manager.get_logger("root")
    logger = log_manager.clone(root_logger, "main")
    log_manager.set_route(logger, logger.Level.INFO, Alarmist(), sys.stderr)

    logger.info("Hello, World!")
    logger.warning("Stay safe out there!")

This example is included in the module. Run ``python -m turberfield.utils.logger`` to see
that these log entries are now in colour on the terminal.

By default, logging goes to sys.stderr.
You can log to a file by passing the necessary path.

.. code-block:: python

    log_manager.set_route(logger, logger.Level.DEBUG, LogAdapter(), pathlib.Path("logger.log"))
    logger.error("I didn't mean that.")
    logger.debug("It doesn't hurt to check.")
    logger.note("Whistle a happy tune!")
    logger.critical(
        "We've run out of disk space!",
        status=http.HTTPStatus.INSUFFICIENT_STORAGE
    )

::

    $ cat logger.log
    2022-05-25 19:11:55.260938|   ERROR|main| I didn't mean that.|
    2022-05-25 19:11:55.261088|   DEBUG|main| It doesn't hurt to check.|
    2022-05-25 19:11:55.261178|    NOTE|main| Whistle a happy tune!|
    2022-05-25 19:11:55.261241|CRITICAL|main| We've run out of disk space!|INSUFFICIENT_STORAGE

"""


import asyncio
from collections import defaultdict
from collections import namedtuple
import datetime
import enum
import functools
import io
import logging
import pathlib
import sys


class Logger:

    Entry = namedtuple("Entry", ("origin", "level", "tokens", "metadata"))
    Level = enum.Enum(
        "Level",
        [(label, getattr(logging, label, 15)) for label in [
            "NOTSET", "DEBUG", "NOTE", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]]
    )

    def __init__(self, name, manager, frame=None):
        self.name = name
        self.manager = manager
        self.frame = frame or [
            "{now}", "{level.name:>8}", "{logger.name}", " {0}"
        ]

    @property
    def metadata(self):
        return {
            "logger": self,
            "now": datetime.datetime.utcnow()
        }

    def format(self, *args, **kwargs):
        for field in self.frame:
            try:
                yield field.format(*args, **kwargs)
            except Exception:
                yield ""

    def entry(self, level, *args, **kwargs):
        metadata = dict(self.metadata, level=level, **kwargs)
        tokens = tuple(self.format(*args, **metadata))
        return self.Entry(self, level, tokens, metadata)

    def log(self, level, *args, **kwargs):
        entry = self.entry(level, *args, **kwargs)
        try:
            self.manager.queue.put_nowait(entry)
        except asyncio.QueueFull:
            pass
        finally:
            self.manager.notify(self)

    debug = functools.partialmethod(log, Level.DEBUG)
    note = functools.partialmethod(log, Level.NOTE)
    info = functools.partialmethod(log, Level.INFO)
    warning = functools.partialmethod(log, Level.WARNING)
    error = functools.partialmethod(log, Level.ERROR)
    critical = functools.partialmethod(log, Level.CRITICAL)


class LogManager:

    endings = {}
    loggers = {}
    routing = defaultdict(set)

    Pair = namedtuple("Pair", ("logger_name", "endpoint_name"))
    Route = namedtuple("Route", ("logger", "level", "adapter", "endpoint"))

    def __init__(
        self, *args,
        defaults: list=None, queue=None, loop=None, executor=None, timeout=None, **kwargs
    ):
        self.defaults = defaults or [self.Route(None, Logger.Level.INFO, LogAdapter(), sys.stderr)]
        self.queue = queue or asyncio.Queue()
        self.loop = loop
        self.timeout = timeout
        self.executor = executor

        self.endpoints = [self.register_endpoint(i) for i in args]

        self.register_endpoint(sys.stderr)
        for route in self.defaults:
            self.register_endpoint(route.endpoint)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        to_close = filter(None, (self.endings.get(i, None) for i in self.endpoints))
        for i in to_close:
            if i is not sys.stderr:
                try:
                    self.wait_for(i.close)
                except Exception as e:
                    sys.stderr.write("Error on exit: ")
                    sys.stderr.write(repr(e))
                    sys.stderr.write("\n")
        return False

    @property
    def pairings(self):
        return [(k, v) for k, v in self.routing.items() if isinstance(k, self.Pair)]

    def register_endpoint(self, obj, registry=None):
        registry = registry if registry is not None else self.endings
        if isinstance(obj, io.TextIOBase):
            try:
                registry[obj.name] = obj
            except AttributeError:
                obj.name = id(obj)
                registry[obj.name] = obj
            finally:
                return obj

        elif isinstance(obj, str):
            obj = pathlib.Path(obj)

        if isinstance(obj, pathlib.Path):
            f = obj.open(mode="at", buffering=1)
            registry[obj] = f
            return obj

    def wait_for(self, func, *args, **kwargs):
        if self.loop:
            return self.loop.run_until_complete(
                asyncio.wait_for(
                    self.loop.run_in_executor(self.executor, func, *args),
                    self.timeout
                )
            )
        else:
            return func(*args, **kwargs)

    def get_logger(self, name, factory=Logger, frame=None, routing=None, registry=None, **kwargs):
        routing = routing or self.defaults
        registry = registry if registry is not None else self.loggers

        if name in registry:
            return registry[name]

        logger = factory(name, self, frame=frame, **kwargs)
        registry[name] = logger

        if not any(pair.logger_name == name for pair, _ in self.pairings):
            for route in routing:
                try:
                    self.set_route(logger, route.level, route.adapter, route.endpoint)
                except Exception:
                    sys.stderr.write(f"Failed to set {route} to {logger}\n")

        return logger

    def clone(self, logger, name, **kwargs):
        routes = [
            r for k, v in self.pairings
            for r in v
            if k.logger_name == logger.name
        ]
        return self.get_logger(name, factory=type(logger), frame=logger.frame, routing=routes)

    def set_route(self, logger, level, adapter, endpoint, replace=True, registry=None):
        registry = registry if registry is not None else self.routing
        endpoint = self.register_endpoint(endpoint)
        try:
            pair = self.Pair(logger.name, endpoint.resolve())
        except AttributeError:
            pair = self.Pair(logger.name, endpoint.name)
        route = self.Route(logger, level, adapter, endpoint)

        if replace:
            registry[pair].clear()

        registry[pair].add(route)
        return route

    def notify(self, client):
        rv = self.queue.qsize()
        while self.queue.qsize():
            entry = self.queue.get_nowait()
            try:
                routes = (
                    r for k, v in self.pairings
                    for r in v
                    if k.logger_name == entry.origin.name
                )
                for route in routes:
                    try:
                        route.adapter.emit(entry, route)
                    except Exception as e:
                        sys.stderr.write("Error in emit: ")
                        sys.stderr.write(repr(e))
                        sys.stderr.write("\n")
            finally:
                self.queue.task_done()

        return rv


class LogAdapter:

    def render(self, entry):
        return "|".join(entry.tokens)

    def emit(self, entry, route):
        try:
            allow = entry.level.value >= route.level.value
        except AttributeError:
            allow = False

        if allow:
            endpoint = entry.origin.manager.endings.get(route.endpoint, route.endpoint)
            text = self.render(entry)
            endpoint.write(text)
            endpoint.write("\n")


class LogLocation(LogManager):

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = pathlib.Path(path)

    @property
    def stat(self):
        return self.wait_for(self.path.stat)


if __name__ == "__main__":
    import http
    import platform
    import re

    logger = LogManager().get_logger("root")
    logger.info("Hello, World!")

    logger.frame += ["{status.name}"]
    logger.info("Situation report", status=http.HTTPStatus.OK)

    class Alarmist(LogAdapter):

        patterns = [
            (re.compile("NOTE"), (234, 0, 255)),
            (re.compile("INFO"), (0, 255, 255)),
            (re.compile("ERROR"), (234, 255, 0)),
            (re.compile("WARNING"), (255, 106, 0)),
            (re.compile("CRITICAL"), (255, 0, 106)),
        ]

        def colour_field(self, field, word):
            if "level" in field:
                r, g, b = next(
                    (c for r, c in self.patterns if r.search(word)),
                    (200, 200, 200)
                )
                return f"\033[38;2;{r};{g};{b}m{word}\033[0m"
            else:
                return word

        def render(self, entry):
            if platform.system().lower() == "windows":
                return super().render(entry)

            return "|".join(
                self.colour_field(f, w)
                for f, w in zip(entry.origin.frame, entry.tokens)
            )


    with LogManager() as log_manager:

        # Once you have configured a logger, you can clone it as the basis of another
        logger = log_manager.clone(log_manager.get_logger("root"), "main")
        log_manager.set_route(logger, logger.Level.INFO, Alarmist(), sys.stderr)

        logger.info("Hello, World!")
        logger.warning("Stay safe out there!")

        log_manager.set_route(logger, logger.Level.DEBUG, LogAdapter(), pathlib.Path("logger.log"))
        logger.error("I didn't mean that.")
        logger.debug("It doesn't hurt to check.")
        logger.note("Whistle a happy tune!")
        logger.critical(
            "We've run out of disk space!",
            status=http.HTTPStatus.INSUFFICIENT_STORAGE
        )
