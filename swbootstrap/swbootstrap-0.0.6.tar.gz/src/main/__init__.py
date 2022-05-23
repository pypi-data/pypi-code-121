import random
import time

import click

from .cmd import bootstrap_cmd


def create_sw_bootstrap() -> click.core.Group:
    random.seed(time.time_ns)
    bootstrap.add_command(bootstrap_cmd)
    return bootstrap


bootstrap = create_sw_bootstrap()
if __name__ == "__main__":
    bootstrap()
