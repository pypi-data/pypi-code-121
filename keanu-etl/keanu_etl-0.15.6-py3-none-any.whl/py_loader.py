import os
import sys
from collections import namedtuple
from glob import glob
from importlib import import_module
from pathlib import Path
from threading import Lock, Thread
from time import time

import click
from pymysql.err import MySQLError
from sqlalchemy.exc import DataError, IntegrityError, InternalError, ProgrammingError

from . import db, tracing

ThreadInfo = namedtuple("ThreadInfo", ["index", "count"])


class PyLoader(tracing.Tags):
    """
    Class that runs load modules, that is Python modules that load some data in keanu database.
    """

    def __init__(self, filename, mode, source, destination):
        super().__init__()
        self.filename = filename

        self.module = PyLoader.import_module(filename)
        self.lock = Lock()

        self.options = {
            "incremental": False,
            "display": False,
            "warn": False,
            "dry_run": False,
            "threads": 1,
        }
        self.options.update(mode)

        self.source = source
        self.destination = destination

        if self.defines("TAGS"):
            if isinstance(self.module.TAGS, dict):
                self.tracing_tags = self.module.TAGS
            else:
                raise click.ClickException(
                    "TAGS in {} should be a dict".format(self.filename)
                )
        else:
            self.tracing_tags = {}

        if self.defines("ORDER"):
            if isinstance(self.module.ORDER, int):
                self.order = self.module.ORDER
            else:
                raise click.ClickException(
                    "ORDER in {} should be a number".format(self.filename)
                )
        else:
            self.order = 100

        if self.defines("IGNORE"):
            self.ignore = self.module.IGNORE
        else:
            self.ignore = not self.defines("execute")

        self.use_transaction = False
        if self.defines("TRANSACTION"):
            self.use_transaction = self.module.TRANSACTION
        if self.defines("TRANSACTION_INCREMENTAL") and self.options['incremental']:
            self.use_transaction = self.module.TRANSACTION_INCREMENTAL

        self.checkpoint = None

    @staticmethod
    def import_module(filename):
        if filename.endswith(".py"):
            mod_name = os.path.splitext(os.path.basename(filename))[0]
            dir = os.path.dirname(os.path.abspath(filename))
            sys.path.insert(0, dir)
            mod = import_module(mod_name)
            sys.path.pop(0)
            return mod
        else:
            raise click.ClickException("Cannot load non-py file {}".format(filename))

    @staticmethod
    def from_directory(sqldir, mode, source, destination):
        files = glob(os.path.join(sqldir, "**/*.py"), recursive=True)
        if len(files) == 0:
            raise click.BadParameter(
                "No py files found in {}".format(sqldir), param_hint="config_or_dir"
            )
        # skip __init__.py
        files = filter(lambda x: os.path.basename(x) != "__init__.py", files)
        scripts = list(map(lambda fn: PyLoader(fn, mode, source, destination), files))
        return scripts

    def __str__(self):
        return "{} ({})".format(self.filename, self.order)

    def delete(self):
        if self.ignore or not self.defines("delete"):
            return
        try:
            yield "py.script.start.delete", {"script": self}
            start_time = time()

            if self.options["dry_run"]:
                return
            with tracing.span(
                    "delete.{}".format(self.filename.replace("/", ".")),
                    tags=self.tracing_tags,
            ):
                self.module.delete(self)
            yield "py.script.end.delete", {"script": self, "time": time() - start_time}

        except KeyboardInterrupt as ctrlc:
            raise ctrlc


    def execute(self):
        if self.ignore:
            return

        yield "py.script.start", {"script": self}
        start_time = time()

        if self.options["dry_run"]:
            return

        with tracing.span(
                "script.{}".format(self.filename.replace("/", ".")),
                tags=self.tracing_tags,
        ):
            result = self.wrap_in_transaction(lambda: self.module.execute(self))

        yield "py.script.end", {
            "script": self,
            "time": time() - start_time,
            "result": result,
        }

    def wrap_in_transaction(self, funct):
        if self.use_transaction:
            inner_funct = funct
            def funct_in_transaction():
                conn = self.destination.connection()
                with conn.begin() as transaction:
                    try:
                        r = inner_funct()
                        return r
                    except KeyboardInterrupt as e:
                        print("rolling back due interrupt")
                        transaction.rollback()
                        raise e

                    except Exception as e:
                        print("rolling back")
                        transaction.rollback()
                        raise e

            funct = funct_in_transaction

        try:
            result = funct()
        except KeyboardInterrupt as e:
            raise click.Abort("aborted.")
        except (
                ProgrammingError,
                IntegrityError,
                MySQLError,
                InternalError,
                DataError,
        ) as e:
            msg = str(e.args[0])
            msg = msg.replace("\\n", "\n")
            click.echo(message=msg, err=True)
            raise click.Abort(msg)

        return result


    @staticmethod
    def slice_for_thread(iterable, thread):
        for i, v in enumerate(iterable):
            if i % thread.count == thread.index:
                yield v

    @staticmethod
    def thread_info(thread_index, thread_count):
        return ThreadInfo(thread_index, thread_count)

    def defines(self, varname):
        return varname in dir(self.module)

    @staticmethod
    def path_to_module(path):
        p = Path(path)

        def strip_py(x):
            if x.endswith(".py"):
                return x[0:-3]
            else:
                return x

        m = ".".join(map(lambda a: strip_py(a), p.parts))

        return m

    def threaded(self, function):
        if self.options["threads"] > 1:

            def execute_then_close_connections(thr):
                try:

                    r = self.wrap_in_transaction(lambda: function(thr))
                    return ("ok", r)
                except Exception as exc:
                    click.echo(exc)
                    return ("error", exc.__class__.__name__, exc.args)
                finally:
                    self.destination.threadsafe_close()
                    self.source.threadsafe_close()


            thr_ct = self.options["threads"]
            threads = [
                Thread(
                    target=execute_then_close_connections, args=(ThreadInfo(i, thr_ct),)
                )
                for i in range(thr_ct)
            ]

            [t.start() for t in threads]

            [t.join() for t in threads]
            # Python multi-threading is very lame.
            # Can't get return value with oh-so-basic threading.Thread :-<
            #  concurrent.futures.ThreadPoolExecutor crashes with SIGSEGV (even official docs examples)
            # TODO: test: from multiprocessing.pool import ThreadPool
            # failures = list(itertools.filterfalse(lambda a: a[0] == 'ok', results))
            # if len(failures) > 0:
            #     f = failures[0]
            #     raise click.Abort("Exception (in thread): {ex} with {args}".format(
            #         ex=f[1], args=f[2]))
            # else:
            #     return list(map(lambda a: a[1], results))

        else:
            return function(ThreadInfo(0, 1))

    def get_checkpoint(self, checkpoint):
        """
        Used to synchronize the checkpoint, which will be max processed id of imput data, between all processing threads. Because input data can grow realtime, we would run into problems if some threads would use a different input boundary.
                This is the value that should also be saved to last_sync tables.
        """
        try:
            self.lock.acquire()
            if self.checkpoint is None:
                self.checkpoint = checkpoint
            return self.checkpoint
        finally:
            self.lock.release()
