import operator
from signal import signal, SIGUSR1
from time import sleep

import click

from . import util
from . import tracing


sighup_received = False


def sighup(_a, _b):
    util.clear_line()
    click.echo("🛬 Received SIGUSR1, stopping as soon as possible...")
    global sighup_received
    sighup_received = True


signal(SIGUSR1, sighup)


class RetryScript(Exception):
    pass


RETRY_COUNT = 3
RETRY_SLEEP = 10


class Batch:
    def __init__(self, mode):
        """
        mode - running mode of this batch. Map containing:
        = {
          incremental - boolean - whether to avoid updating data that did not change (optimization)
          order - string - order specification, limiting scripts to run
          dry_run - boolean - if set, don't execute statements for real
          display - boolean - display more information
          warn - boolean - display warnings (supressed by default)
          rewind - boolean - run in rewind mode
          threads - int - number of threads for parallel processing
          }
        """
        self.mode = {
            "incremental": False,
            "display": False,
            "warn": False,
            "dry_run": False,
            "rewind": False,
            "threads": 1,
        }

        self.mode.update(mode)
        self.sources = []
        self.destination = None
        self.scripts = []

    @property
    def is_dry_run(self):
        return self.mode["dry_run"]

    def add_source(self, source):
        source.batch = self
        self.sources.append(source)

    def add_destination(self, destination):
        destination.batch = self
        self.destination = destination

    def add_transform(self, transform):
        """
        Gets all scripts from this transform and stores them in sorted order
        """
        self.scripts += transform.get_scripts()
        if "order" in self.mode:
            self.scripts = util.filter_scripts_by_order(
                self.scripts, self.mode["order"]
            )
        self.scripts = self.sort(self.scripts)
        if self.mode["rewind"]:
            self.scripts.reverse()

    def execute(self):
        with tracing.transaction("batch", tags=self.tracer_tags):
            for scr in self.scripts:
                for tries in range(RETRY_COUNT):
                    try:
                        if self.mode["rewind"] == False:
                            for e, d in scr.execute():
                                yield e, d
                        else:
                            for e, d in scr.delete():
                                yield e, d

                        if sighup_received:
                            raise click.Abort("Stopped gracefully due to USR1 signal")

                        break  # from retry loop
                    except RetryScript as rse:
                        if tries + 1 == RETRY_COUNT:
                            raise click.Abort("Too many retries, aborting") from rse
                        else:
                            click.echo(
                                "Encountered error that can be retried: {}.\n😴  Sleeping 10 seconds....".format(
                                    rse.__cause__
                                )
                            )
                            sleep(RETRY_SLEEP)
                            click.echo("Retrying....")

    def find_source(self, criteria):
        for s in reversed(self.sources):
            if criteria(s):
                return s
        return None

    def find_source_by_name(self, name):
        return self.find_source(lambda s: s.name == name)

    @staticmethod
    def sort(scripts):
        scripts.sort(key=operator.attrgetter("order"))
        return scripts

    @property
    def tracer_tags(self):
        return {
            "mode": "delete" if self.mode["rewind"] else "load",
            "incremental": self.mode["incremental"] == True,
        }
