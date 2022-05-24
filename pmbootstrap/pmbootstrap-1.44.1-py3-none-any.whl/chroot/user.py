# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import pmb.chroot.root
import pmb.helpers.run


def user(args, cmd, suffix="native", working_dir="/", output="log",
         output_return=False, check=None, env={}, auto_init=True):
    """
    Run a command inside a chroot as "user". We always use the BusyBox
    implementation of 'su', because other implementations may override the PATH
    environment variable (#1071).

    :param env: dict of environment variables to be passed to the command, e.g.
                {"JOBS": "5"}
    :param auto_init: automatically initialize the chroot

    See pmb.helpers.run_core.core() for a detailed description of all other
    arguments and the return value.
    """
    if "HOME" not in env:
        env["HOME"] = "/home/pmos"

    flat_cmd = pmb.helpers.run.flat_cmd(cmd, env=env)
    cmd = ["busybox", "su", "pmos", "-c", flat_cmd]
    return pmb.chroot.root(args, cmd, suffix, working_dir, output,
                           output_return, check, {}, auto_init)


def exists(args, username, suffix="native"):
    """
    Checks if username exists in the system

    :param username: User name
    :returns: bool
    """
    output = pmb.chroot.root(args, ["getent", "passwd", username],
                             suffix, output_return=True, check=False)
    return len(output) > 0
