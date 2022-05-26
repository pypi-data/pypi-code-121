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

from signal import SIGINT, getsignal, signal
from types import FrameType, TracebackType
from typing import Optional, Tuple, Type


class DelayedKeyboardInterrupt:

    def __enter__(self) -> None:
        self.signal_received: Optional[Tuple[int, Optional[FrameType]]] = None
        self.old_handler = getsignal(SIGINT)
        signal(SIGINT, self.handler)

    def handler(self, signum: int, frame: Optional[FrameType]) -> None:
        self.signal_received = (signum, frame)

    def __exit__(self,
                 _exc_type: Optional[Type[BaseException]],
                 _exc_value: Optional[BaseException],
                 _traceback: Optional[TracebackType]) -> None:
        signal(SIGINT, self.old_handler)
        if self.signal_received and callable(self.old_handler):
            self.old_handler(*self.signal_received)
