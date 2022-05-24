import random
import time

import click

from .cmd import bootstrap_cmd

def create_sw_bootstrap() -> click.core.Group:
    @click.group()
    @click.version_option(version='0.0.1')
    @click.option("-v", "--verbose", count=True, help="verbose for log")
    def bs(verbose: bool) -> None:
        print('hello')
    random.seed(time.time_ns)
    bs.add_command(bootstrap_cmd)
    return bs


bootstrap = create_sw_bootstrap()
if __name__ == "__main__":
    bootstrap()
