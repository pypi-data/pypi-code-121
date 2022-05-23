#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
from cgbeacon2 import __version__
from cgbeacon2.server import create_app
from flask.cli import FlaskGroup

from .add import add
from .delete import delete
from .update import update


@click.version_option(__version__)
@click.group(
    cls=FlaskGroup,
    create_app=create_app,
    invoke_without_command=False,
    add_default_commands=True,
    add_version_option=False,
)
def cli(**_) -> None:
    """Base command for invoking the command line"""
    pass


cli.add_command(add)
cli.add_command(delete)
cli.add_command(update)
