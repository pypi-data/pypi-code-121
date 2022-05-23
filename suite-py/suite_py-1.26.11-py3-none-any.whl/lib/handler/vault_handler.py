# -*- encoding: utf-8 -*-
import os
import subprocess
import sys
from subprocess import CalledProcessError

from suite_py.lib import logger


class VaultHandler:
    def __init__(self, repo, config):
        self._repo = repo
        self._projects_home = config.user["projects_home"]
        self._path = os.path.join(self._projects_home, repo)

    def exec(self, profile, command, additional_args=""):
        try:
            c = subprocess.Popen(  # pylint: disable=consider-using-with
                f"aws-vault exec {profile} {additional_args} -- {command}",
                stdout=subprocess.PIPE,
                shell=True,
                cwd=self._path,
            )  # .stdout.read()
            c.wait()
            return c
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)
