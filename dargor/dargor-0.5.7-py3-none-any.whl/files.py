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

from contextlib import contextmanager
from fcntl import LOCK_EX, LOCK_NB, flock
from typing import IO, AnyStr, Iterator


@contextmanager
def lock_and_open_for_write(fname: str,
                            mode: str = 'w') -> Iterator[IO[AnyStr]]:
    try:
        fd = None
        lock_fd = open(f'{fname}.lock', 'w')
        flock(lock_fd, LOCK_EX | LOCK_NB)
        fd = open(fname, mode)
        yield fd
    finally:
        if fd is not None:
            fd.flush()
            fd.close()
        lock_fd.close()
