# -*- coding: utf-8 -*-

from attr import attrs, attrib
from tuxsuite.cli.argparse import setup_parser
from tuxsuite.cli.config import load_config


class defaults:
    targets = [
        "config",
        "debugkernel",
        "dtbs",
        "kernel",
        "modules",
        "xipkernel",
    ]


@attrs(kw_only=True)
class ResultState:
    state = attrib()
    status = attrib(default=None)
    message = attrib()
    warnings = attrib(default=0)
    errors = attrib(default=0)
    icon = attrib()
    cli_color = attrib()
    final = attrib(default=False)


result_states = {
    "queued": ResultState(
        state="queued",
        message="Queued",
        icon="⏳",
        cli_color="white",
    ),
    "waiting": ResultState(
        state="waiting",
        message="Waiting",
        icon="⏳",
        cli_color="white",
    ),
    "provisioning": ResultState(
        state="provisioning",
        message="Provisioning",
        icon="⚙️ ",
        cli_color="white",
    ),
    "building": ResultState(
        state="building",
        message="Building",
        icon="🚀",
        cli_color="cyan",
    ),
    "running": ResultState(
        state="running",
        message="Running",
        icon="🚀",
        cli_color="cyan",
    ),
}


def tuxcli_load():
    cfg = load_config()
    options = setup_parser(cfg.group, cfg.project).parse_args()
    return (cfg, options)
