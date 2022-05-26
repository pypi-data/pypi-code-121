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

import asyncio
import sys
import traceback
from contextlib import suppress
from types import TracebackType
from typing import (
    Any,
    Dict,
    Optional,
    Type,
)

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import Python3TracebackLexer


def excepthook(exc_type: Optional[Type[BaseException]],
               exc_value: Optional[BaseException],
               exc_traceback: Optional[TracebackType]) -> None:
    tb = ''.join(traceback.format_exception(exc_type,
                                            exc_value,
                                            exc_traceback))
    lexer = Python3TracebackLexer(stripall=True, tabsize=4)
    formatter = Terminal256Formatter(style='vim', bg='dark')
    print(highlight(tb, lexer, formatter).strip(), file=sys.stderr)


def asyncio_exception_handler(loop: asyncio.AbstractEventLoop,
                              context: Dict[str, Any]) -> None:
    with suppress(KeyError):
        e = context['exception']
        excepthook(type(e), e, e.__traceback__)
    loop.default_exception_handler(context)


def install() -> None:
    sys.excepthook = excepthook
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(asyncio_exception_handler)
