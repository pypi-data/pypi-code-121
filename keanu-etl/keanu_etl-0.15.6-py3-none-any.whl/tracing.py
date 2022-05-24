from atexit import register
from getpass import getuser
from time import sleep
from os import environ
from contextlib import contextmanager
import sentry_sdk

if 'SENTRY_DSN' in environ:
    sentry_sdk.init(environ['SENTRY_DSN'], traces_sample_rate=1.0, _experiments={"max_spans": 10000})


class Tags:
    def __init__(self):
        self._tracing_tags = {}

    # pylint: disable=no-member
    @property
    def tracing_tags(self):
        t = {
            "incremental": self.options["incremental"] == True,
        }
        if self.source:
            t["source_name"] = self.source.name
        if self.destination:
            t["destination_name"] = self.destination.name
        t.update(self._tracing_tags)
        return t

    @tracing_tags.setter
    def tracing_tags(self, tags):
        self._tracing_tags = tags

@contextmanager
def transaction(description, tags={}):
    with sentry_sdk.start_transaction() as t:
        t.name = description
        for k,v in tags.items():
            t.set_tag(k, v)
        yield t

@contextmanager
def span(description, tags={}):
    with sentry_sdk.start_span() as s:
        s.description = description
        
        for k,v in tags.items():
            s.set_tag(k,v) 
        yield s
