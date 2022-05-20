from __future__ import annotations

import platform

from collections import deque
from enum import Enum, unique

from .getwch import getwch
from . import constant

if platform.system() == "Windows":
    # Code to move the cursor on Windows inspired by colorama by tartley
    # GitHub: https://github.com/tartley/colorama/blob/master/colorama/win32.py
    from ctypes import windll, wintypes, Structure, byref

    class ConsoleInfo(Structure):
        _fields_ = [("dwSize", wintypes._COORD), ("dwCursorPosition", wintypes._COORD),
                    ("wAttributes", wintypes.WORD), ("srWindow", wintypes.SMALL_RECT),
                    ("dwMaximumWindowSize", wintypes._COORD)]


@unique
class Key(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Input:
    '''
    # Input

    A buffered input class.

    It serves as the base class for all the other input classes.
    '''

    _history: list[str] = []
    _buffer: deque[str] = deque()
    _right_buffer: deque[str] = deque()
    _system = platform.system()

    def __init__(self):
        if self._system == "Windows":
            self._console_info = ConsoleInfo()
            self._handle = windll.kernel32.GetStdHandle(-11)
            self._directions = {"K": Key.LEFT, "M": Key.RIGHT, "H": Key.UP, "P": Key.DOWN}
        else:
            self._directions = {"D": Key.LEFT, "C": Key.RIGHT, "A": Key.UP, "B": Key.DOWN}

        self._cursor_left = 0
        self._search_index = 0

    def __call__(self, prompt: str = "") -> str:
        '''
        The `buffer_input()` reads the user input and saves it in a (shared between input types)
        buffer while the user is typing.

        Call `buffer_input.get_input_buffer()` to get the current buffer.

        ## Arguments

        prompt: str [optional] = what to print before asking for input. default value = "".

        string: str [return] = returns a string with the user typed input.

        ## Usage

        e.g.
        ```python
          value = buffer_input("Enter a number: ")
        ```
        '''

        if prompt != "":
            print(prompt, end="", flush=True)

        while True:
            if constant.CURRENT_INPUT is not self:
                constant.CURRENT_INPUT = self

            char = getwch()

            if char == "\r":
                break
            elif char == "\x03":
                self._buffer.clear()
                raise KeyboardInterrupt

            if self._system == "Windows":
                if char == "\x08":
                    if len(self._buffer) > 0:
                        self._buffer.pop()
                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        out = ("\r" + " "*len_ + "\r" + prompt
                               + "".join(self._buffer + self._right_buffer))
                        print(out, end="", flush=True)
                        self._move_cursor()
                elif char == "\x00":
                    direction = self._directions.get(getwch(), None)

                    if direction == Key.LEFT:
                        if len(self._buffer) + len(self._right_buffer) == self._cursor_left:
                            continue

                        windll.kernel32.GetConsoleScreenBufferInfo(self._handle,
                                                                   byref(self._console_info))
                        pos = self._console_info.dwCursorPosition
                        new = wintypes._COORD(pos.X - 1, pos.Y)
                        windll.kernel32.SetConsoleCursorPosition(self._handle, new)
                        self._cursor_left += 1
                        self._right_buffer.appendleft(self._buffer.pop())
                    elif direction == Key.RIGHT:
                        if self._cursor_left == 0:
                            continue

                        windll.kernel32.GetConsoleScreenBufferInfo(self._handle,
                                                                   byref(self._console_info))
                        pos = self._console_info.dwCursorPosition
                        new = wintypes._COORD(pos.X + 1, pos.Y)
                        windll.kernel32.SetConsoleCursorPosition(self._handle, new)
                        self._cursor_left -= 1
                        self._buffer.append(self._right_buffer.popleft())
                    elif direction == Key.UP:
                        if len(self._history) == self._search_index * -1:
                            continue

                        self._search_index -= 1
                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        self._buffer.clear()
                        self._right_buffer.clear()
                        out = "\r" + " "*len_ + "\r" + prompt + self._history[self._search_index]
                        print(out, end="", flush=True)
                        self._buffer += deque(self._history[self._search_index])
                    elif direction == Key.DOWN:
                        if self._search_index < 0:
                            self._search_index += 1

                        if self._search_index == 0:
                            continue

                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        self._buffer.clear()
                        self._right_buffer.clear()
                        out = "\r" + " "*len_ + "\r" + prompt + self._history[self._search_index]
                        print(out, end="", flush=True)
                        self._buffer += deque(self._history[self._search_index])
                    elif direction is None:
                        continue
                else:
                    self._buffer.append(char)
                    print(char + "".join(self._right_buffer), end="", flush=True)
                    self._move_cursor()
            else:
                if char == "\x7f":
                    if len(self._buffer) > 0:
                        self._buffer.pop()
                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        out = ("\r" + " "*len_ + "\r" + prompt
                               + "".join(self._buffer + self._right_buffer))
                        out += self._move_cursor()
                        print(out, end="", flush=True)
                elif char == "\x1b":
                    getwch()
                    direction = self._directions.get(getwch(), None)

                    if direction == Key.LEFT:
                        if len(self._buffer) + len(self._right_buffer) == self._cursor_left:
                            continue

                        print("\033[D", end="", flush=True)
                        self._cursor_left += 1
                        self._right_buffer.appendleft(self._buffer.pop())
                    elif direction == Key.RIGHT:
                        if self._cursor_left == 0:
                            continue

                        print("\033[C", end="", flush=True)
                        self._cursor_left -= 1
                        self._buffer.append(self._right_buffer.popleft())
                    elif direction == Key.UP:
                        if len(self._history) == self._search_index * -1:
                            continue

                        self._search_index -= 1
                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        self._buffer.clear()
                        self._right_buffer.clear()
                        out = "\r" + " "*len_ + "\r" + prompt + self._history[self._search_index]
                        print(out, end="", flush=True)
                        self._buffer += deque(self._history[self._search_index])
                    elif direction == Key.DOWN:
                        if self._search_index < 0:
                            self._search_index += 1

                        if self._search_index == 0:
                            continue

                        len_ = len(self._buffer) + len(self._right_buffer) + len(prompt) + 1
                        self._buffer.clear()
                        self._right_buffer.clear()
                        out = "\r" + " "*len_ + "\r" + prompt + self._history[self._search_index]
                        print(out, end="", flush=True)
                        self._buffer += deque(self._history[self._search_index])
                    elif direction is None:
                        continue
                else:
                    self._buffer.append(char)
                    print(char + "".join(self._right_buffer) + self._move_cursor(), end="",
                          flush=True)

        print()
        string = ""

        while len(self._buffer) > 0:
            string += self._buffer.popleft()

        while len(self._right_buffer) > 0:
            string += self._right_buffer.popleft()

        self._history.append(string)
        self._cursor_left = 0
        self._search_index = 0
        return string

    def _move_cursor(self) -> str:
        if self._cursor_left > 0:
            if self._system == "Windows":
                windll.kernel32.GetConsoleScreenBufferInfo(self._handle, byref(self._console_info))
                pos = self._console_info.dwCursorPosition
                new = wintypes._COORD(pos.X - self._cursor_left, pos.Y)
                windll.kernel32.SetConsoleCursorPosition(self._handle, new)
                return ""
            else:
                return "\033[D" * self._cursor_left
        else:
            return ""

    @classmethod
    def get_input_buffer(cls) -> deque[str]:
        '''
        Get the currently saved (shared between input types) buffer.

        Note: the buffer is not shared between thread safe inputs and normal inputs.

        ## Arguments

        buffer: deque[str] [return] = returns a copy of the buffer as a string deque.
        '''

        if not isinstance(constant.CURRENT_INPUT, Input) and constant.CURRENT_INPUT is not None:
            raise TypeError("the global constant 'CURRENT_INPUT' was reassigned")
        elif constant.CURRENT_INPUT is None:
            return cls._buffer.copy() + cls._right_buffer.copy()
        else:
            move = [] if cls._system == "Windows" else [constant.CURRENT_INPUT._move_cursor()]
            return cls._buffer.copy() + cls._right_buffer.copy() + deque(move)


buffer_input = Input()
