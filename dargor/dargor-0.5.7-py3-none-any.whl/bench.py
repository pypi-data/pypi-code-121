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

import datetime as dt
from contextlib import contextmanager
from typing import Any, Callable, Iterator

_printer = print


def set_printer(fn: Callable[..., Any]) -> None:
    global _printer
    _printer = fn


def reset_printer() -> None:
    global _printer
    _printer = print


@contextmanager
def bench(msg: str) -> Iterator[None]:
    error = None
    try:
        start = dt.datetime.now()
        yield
    except Exception as e:
        error = e
        raise
    finally:
        if not error:
            stop = dt.datetime.now()
            time = (stop - start).total_seconds()
            m = f'{time:.3f} seconds'
        else:
            m = repr(error)
        _printer(f'{msg} time: {m}')
