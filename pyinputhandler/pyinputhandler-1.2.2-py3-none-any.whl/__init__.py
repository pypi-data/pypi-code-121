'''
# Input Handler Module

The `inputhandler` module from the `pyinputhandler` package.

It contains various buffered inputs.

## Usage

You can import the simple `buffer_input()` and use it just like a normal input.

e.g.
```python
  from inputhandler import buffer_input


  value = buffer_input("Enter a number: ")
```

You can also use it in an asynchronous operation and read its buffer with `get_input_buffer()`.

e.g.
```python
  ...  # your async code
  buffer = get_input_buffer()
```
'''

from __future__ import annotations

import threading

from collections import deque

from .getwch import getwch
from .buffer_input import Input, buffer_input
from .input_types import try_input, safe_input, safe_try_input
from . import input_types
from . import constant


def get_input_buffer() -> deque[str]:
    '''
    An alternative to get the shared buffer input. Returns a buffer as a string deque.
    '''

    return buffer_input.get_input_buffer()


def get_safe_buffer() -> deque[str]:
    '''
    An alternative to get the safe buffer input. Returns a buffer as a string deque.
    '''

    return safe_input.get_input_buffer()


def set_lock(lock: threading.Lock):
    '''
    Sets the `safe_input()` and `safe_try_input()` locks with the provided `lock`.
    '''

    if not isinstance(lock, threading.Lock):
        raise TypeError("lock must be a threading.Lock instance")

    safe_input._input_lock = lock
    safe_try_input._input_lock = lock
    input_types.ThreadSafeInput._input_lock = lock
    input_types.ThreadSafeTryInput._input_lock = lock


def fix_cursor(input_: Input = None):
    '''
    Fixes the cursor position on the console.
    '''

    if isinstance(input_, Input):
        input_._move_cursor()
    elif isinstance(constant.CURRENT_INPUT, Input) or constant.CURRENT_INPUT is None:

        if constant.CURRENT_INPUT is not None:
            constant.CURRENT_INPUT._move_cursor()
    else:
        raise TypeError("the global constant 'CURRENT_INPUT' was reassigned")
