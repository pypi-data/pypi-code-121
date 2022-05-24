#!/usr/bin/env python

import os
import sys
import click
import glob
import json
import re
import getpass
import traceback
import importlib
import string
import types
import platform
from datetime import datetime
from collections import OrderedDict
from time import strftime, localtime
import logging
from functools import update_wrapper

from enrichsdk.commands import Config, RunManager
from enrichsdk.commands.helper import extend_run_commandset
from enrichsdk.commands import log


@click.group()
@click.pass_context
@click.option("--debug/--no-debug", default=False)
@click.option("--readonly/--no-readonly", default=False)
@click.option("--show-metadata/--no-show-metadata", default=False)
@click.option("-s", "--settings", help="configuration file", default=None)
def main(ctx, debug, readonly, show_metadata, settings):
    """
    Managed command execution.

    This is to ensure repeated adhoc commands have a place to
    go to, and to log all such commands. Further the outputs
    of the commands can be downloaded from the GUI.
    """

    if settings is None:
        tries = [
            os.path.expanduser("~/.enrichcmd-settings.json"),
            ".enrichcmd-settings.json",
        ]

        if "ENRICH_ETC" in os.environ:
            tries.append(
                os.path.join(os.environ["ENRICH_ETC"], "enrichcmd-settings.json")
            )

        for t in tries:
            if os.path.exists(t):
                settings = t
                break

        # If nothing matches, the use the default
        if settings is None:
            settings = tries[0]

    # Setup logging...
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)

    # => Load the global configuration..
    config = Config(
        {
            "debug": debug,
            "readonly": readonly,
            "show_metadata": show_metadata,
            "settings": settings,
        }
    )
    ctx.obj = config

    if ctx.invoked_subcommand not in ["configure"]:
        global _run
        config.configure(settings)
        extend_run_commandset(_run, config)

    # Disable whatever initial logging is there...
    log.logging_clear()


@main.command("configure")
@click.argument("action", type=click.Choice(["init", "show"]))
@click.pass_context
def _configure(ctx, action):
    """
    Initialize the enrichcmd-settings.json

    The settings is required to tell enrichcmd where to
    pickup the commands etc. And more
    """

    config = ctx.obj

    defaults = OrderedDict(
        [
            ("enrich_root", "~/enrich"),
            ("runid", "run-%Y%m%d-%H%M%S-%(username)s"),
            ("rundir", "%(enrich_data)s/_commands/%(runid)s"),
            ("outputdir", "%(rundir)s/output"),
            ("log", "%(rundir)s/log.json"),
            ("metadata", "%(rundir)s/metadata.json"),
            ("libraries", ["%(enrich_root)s/customers/alpha/commands"]),
            (
                "args",
                OrderedDict([("command1", {"path": "%(enrich_data)s/acme/Project"})]),
            ),
        ]
    )

    settings = config.settings
    if action == "init" and os.path.exists(settings):
        print(
            "Error! Settings file {} exists. Not overwriting. Please remove".format(
                settings
            )
        )
        return

    if action == "show" and not os.path.exists(settings):
        print(
            "Error! Settings file {} does not exists. Please create one using 'configure init'".format(
                settings
            )
        )
        return

    if action == "init":
        with open(settings, "w") as fd:
            json.dump(defaults, fd, indent=4)
            print("Created a default settings ({}). Please edit.".format(settings))
    else:
        print(settings)
        print("=====================")
        content = open(settings).read()
        print(content)


@main.command("history")
@click.option("-n", default=10, help="How many entries to show")
@click.pass_obj
def _history(config, n):
    """
    Show history of past commands
    """
    mgr = RunManager({"command_root": config.command_root})

    mgr.show_history(n)


@main.group("run")
def _run():
    """
    Auditable command execution framework

    A number of commands are supported to process partial data.
    """
    pass


if __name__ == "__main__":
    main()
