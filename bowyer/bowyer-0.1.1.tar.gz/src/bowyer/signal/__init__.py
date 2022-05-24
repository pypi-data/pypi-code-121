# -*- coding: utf-8 -*-
"""
Package of bowyer control signals.

---
type:
    python_extension

name_extension:
    bowyer.signal
...

"""


import cython


continue_ok:        cython.int = 0
exit_ex_immediate:  cython.int = 1  # Immediate exceptional shutdown (e.g. fatal nonrecoverable error).
exit_ex_controlled: cython.int = 2  # Controlled exceptional shutdown.
exit_ok_controlled: cython.int = 3  # Controlled nominal shutdown.
control_reset:      cython.int = 4  # Reset and retry
control_pause:      cython.int = 5
control_step:       cython.int = 6

exit = (
    exit_ex_immediate,
    exit_ex_controlled,
    exit_ok_controlled)

reset = (
    control_reset,)

immediate = (
    exit_ex_immediate,)

controlled = (
    exit_ex_controlled,
    exit_ok_controlled,
    control_reset,
    control_pause,
    control_step)
