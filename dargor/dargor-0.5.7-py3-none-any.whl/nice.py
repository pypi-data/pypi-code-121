#! /usr/bin/env python3
#
# Copyright (c) 2022, Gabriel Linder <linder.gabriel@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import atexit
import logging
import os
import subprocess  # nosec
from time import sleep


def _write_autogroup(n: int) -> None:
    data = str(n)
    while True:
        try:  # pylint: disable=R8203
            with open('/proc/self/autogroup', 'w') as f:  # pylint: disable=W8201 # noqa: E501
                f.write(data)
            break
        except FileNotFoundError:
            # no autogroup support in kernel
            break
        except BlockingIOError:
            # race condition at exit
            sleep(.1)


atexit.register(_write_autogroup, 0)


def _run(cmd: str) -> None:
    try:
        r = subprocess.run(cmd.split(' '))  # nosec
        r.check_returncode()
    except Exception:
        logging.warning('Error while running: %s', cmd, exc_info=True)


def ionice() -> None:
    _run(f'ionice -c 3 -p {os.getpid()}')


def sched_idle() -> None:
    _run(f'chrt -i -p 0 {os.getpid()}')


def nice() -> None:
    os.nice(19)
    _write_autogroup(19)


def install() -> None:
    ionice()
    sched_idle()
    nice()


if __name__ == '__main__':
    print('[93m>>> [94mbefore[0m')
    _run('sched-idle -d')
    install()
    print('[93m>>> [94mafter[0m')
    _run('sched-idle -d')
