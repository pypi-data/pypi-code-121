# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from __future__ import print_function

import argparse
import os
import subprocess
import sys

INTERPRETER = os.path.realpath(sys.executable)


def fix_interpreter_permissions():
    args = _parse_args()
    _check_filetype()
    if not args.modify_interpreter:
        _warn_and_exit()
    _run()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--modify-interpreter",
        help="modify permissions for your python interpreter",
        action="store_true",
    )
    return parser.parse_args()


def _check_filetype():
    """
    Sanity check: if we don't see a Mach-O file format for the python
    interpreter, we may be about to make modifications with unknown effects.

    This check is not particularly robust, but it's about as good as we
    can do without significantly more effort (or a new dependency).
    """
    print(f"found interpreter: {INTERPRETER}")
    print("verifying interpreter filetype - expecting Mach-O")
    file_info = subprocess.check_output(["file", INTERPRETER]).decode().rstrip()
    print(file_info)

    if "Mach-O" not in file_info:
        raise RuntimeError("interpreter isn't a Mach-O executable")


def _warn_and_exit():
    warning_msg = """

################################### WARNING ###################################

This operation will modify the permissions of your python interpreter to allow
Contrast to apply its instrumentation. This is a workaround for an issue
specific to OSX python builds. `pyenv` is a popular tool that may lead to this
circumstance.

No known prebuilt installations of python have this issue. If you think you've
found one, please contact support@contrastsecurity.com.

This is a permanent in-place modification to your python interpreter. The real
path of your current interpreter is:

{}

If you wish to continue, please rerun this command with `--modify-interpreter`.
Exiting - no modifications performed.

###############################################################################

""".format(
        INTERPRETER
    )
    print(warning_msg)
    sys.exit(1)


def _run():
    print("found --modify-interpreter command line option")
    print(f"the following interpreter will be modified:\n{INTERPRETER}\n")

    byte_7 = subprocess.Popen(["echo", "-n", "\x07"], stdout=subprocess.PIPE)
    subprocess.check_call(
        [
            "dd",
            f"of={INTERPRETER}",
            "bs=1",
            "seek=160",
            "count=1",
            "conv=notrunc",
        ],
        stdin=byte_7.stdout,
    )

    print(
        "\nSuccess! Your interpreter is now compatible with Contrast's instrumentation."
    )
