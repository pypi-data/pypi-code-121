from __future__ import annotations

import threading
from collections import deque

from .buffer_input import Input


class TryInput(Input):
    '''
    # TryInput

    A buffered input that checks for type.

    It inherits from `Input`.
    '''

    def __init__(self):
        super().__init__()

    def __call__(self, prompt: str = "", *, cast: type | None = None, default=None):
        '''
        The `try_input()` reads the user input like `buffer_input()`.

        Call `try_input.get_input_buffer()` to get the current buffer.

        Additionally, if `cast` is provided, it will try to cast the result into that type and if
        it fails it will returm `default` (or None in case it wasn't provided).

        ## Arguments

        prompt: str [optional] = what to print before asking for input. default value = "".

        named arguments:
        * cast: type | None [optional] = what to cast the input value to. default = None.
        * default: Any | None [optional] = what to return in case the cast fails. default = None.

        string: str | Any | None [return] = returns a string with the user input or, if it was
        provided, the user input casted into `cast`. if the casting fails it returns `default`.

        ## Usage

        e.g.
        ```python
          number = try_input("Enter a number: ", cast=int, default=0)
        ```
        '''

        if cast is None:
            return super().__call__(prompt)

        try:
            return cast(super().__call__(prompt))
        except ValueError:
            return default


class ThreadSafeInput(Input):
    _input_lock = threading.Lock()
    _history = []
    _buffer = deque()
    _right_buffer = deque()

    def __init__(self):
        super().__init__()

    def __call__(self, prompt: str = ""):
        '''
        The `safe_input()` reads the user input like `buffer_input()` but providing (or attempting)
        thread safety.

        Call `safe_input.get_input_buffer()` to get the current buffer. This buffer is not shared
        between other (non thread safe) input types.

        ## Arguments

        prompt: str [optional] = what to print before asking for input. default value = "".

        string: str | Any | None [return] = returns a string with the user input or, if it was
        provided, the user input casted into `cast`. if the casting fails it returns `default`.

        ## Usage

        e.g.
        ```python
          value = safe_input("Enter a number: ")
        ```
        '''

        with self._input_lock:
            return super().__call__(prompt)


class ThreadSafeTryInput(TryInput):
    _input_lock = ThreadSafeInput._input_lock
    _history = ThreadSafeInput._history
    _buffer = ThreadSafeInput._buffer
    _right_buffer = ThreadSafeInput._right_buffer

    def __init__(self):
        super().__init__()

    def __call__(self, prompt: str = "", *, cast: type | None = None, default=None):
        '''
        The `safe_input()` reads the user input like `buffer_input()` but providing (or attempting)
        thread safety.

        Call `safe_input.get_input_buffer()` to get the current buffer. This buffer is not shared
        between other (non thread safe) input types.

        Additionally, if `cast` is provided, it will try to cast the result into that type and if
        it fails it will returm `default` (or None in case it wasn't provided).

        ## Arguments

        prompt: str [optional] = what to print before asking for input. default value = "".

        named arguments:
        * cast: type | None [optional] = what to cast the input value to. default = None.
        * default: Any | None [optional] = what to return in case the cast fails. default = None.

        string: str | Any | None [return] = returns a string with the user input or, if it was
        provided, the user input casted into `cast`. if the casting fails it returns `default`.

        ## Usage

        e.g.
        ```python
          number = safe_try_input("Enter a number: ", cast=int, default=0)
        ```
        '''

        with self._input_lock:
            return super().__call__(prompt, cast=cast, default=default)


try_input = TryInput()
safe_input = ThreadSafeInput()
safe_try_input = ThreadSafeTryInput()
