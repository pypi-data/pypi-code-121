# -*- coding: utf-8 -*-
from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.symbol import CHECKMARK, CROSSMARK


class Status:
    def __init__(self, project, config):
        self._project = project
        self._captainhook = CaptainHook(config)

    def run(self):
        with Halo(text="Contacting Captainhook...", spinner="dots", color="magenta"):
            staging_status = self._captainhook.status(self._project, "staging").json()
            production_status = self._captainhook.status(
                self._project, "production"
            ).json()

        _forge_message(staging_status, "staging")
        _forge_message(production_status, "production")


def _forge_message(status, env):
    if status["locked"]:
        if status["by"] == "":
            logger.error(f"{CROSSMARK} {env}\n      locked")
        else:
            logger.error(f"{CROSSMARK} {env}\n      locked by {status['by']}")
    else:
        logger.info(f"{CHECKMARK} {env}\n      not locked")
