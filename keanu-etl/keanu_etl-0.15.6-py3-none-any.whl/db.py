import threading
from urllib.parse import urlparse

import click
from sqlalchemy import create_engine


def url_to_schema(url):
    if url is None:
        return None
    return urlparse(url).path[1:]


def get_engine(url, dry_run=False):
    """dry_run - if true, use DryRunEngine"""
    if dry_run:
        return DryRunEngine()
    else:
        return create_engine(url, pool_size=2, max_overflow=30)



class DryRunEngine:
    """
    Helper DB engine class which can be used during dry runs.
    It allows to leave the code using with transaction.begin() blocks also in the dry run.
    In such case it will just run the with block.
    """
    name = "mysql"

    @property
    def engine(self):
        return self

    def connect(self):
        return self

    def begin(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self

    def abort(self):
        click.echo("Aborting dry run transaction")

    def execute(self, sql):
        return self

    def fetchone(self):
        return []

    def rowcount(self):
        return 0
