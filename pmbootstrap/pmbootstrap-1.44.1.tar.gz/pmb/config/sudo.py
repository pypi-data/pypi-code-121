# Copyright 2022 Anjandev Momi
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import shutil


def which_sudo():
    """
    Find whether sudo or doas is installed for commands that require root.
    Allows user to override preferred sudo with PMB_SUDO env variable.
    """
    supported_sudos = ['doas', 'sudo']

    user_set_sudo = os.getenv("PMB_SUDO")
    if user_set_sudo is not None:
        if shutil.which(user_set_sudo) is None:
            raise RuntimeError("PMB_SUDO environmental variable is set to"
                               f" {user_set_sudo} but pmbootstrap cannot find"
                               " this command on your system.")
        return user_set_sudo

    for sudo in supported_sudos:
        if shutil.which(sudo) is not None:
            return sudo

    raise RuntimeError("Can't find sudo or doas required to run pmbootstrap."
                       " Please install sudo, doas, or specify your own sudo"
                       " with the PMB_SUDO environmental variable.")
