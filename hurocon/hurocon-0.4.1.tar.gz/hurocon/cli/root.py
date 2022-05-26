import click
from click_didyoumean import DYMGroup

from .. import meta


@click.group(cls=DYMGroup)
@click.version_option(meta.version)
def cli():
    """ Command line interface for Huawei LTE routers """
