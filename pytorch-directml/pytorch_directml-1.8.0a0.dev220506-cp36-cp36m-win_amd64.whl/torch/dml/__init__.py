r"""
The torch.dml package contains data structures for multi-dimensional
tensors and defines mathematical operations over these tensors.
Additionally, it provides many utilities for efficient serializing of
Tensors and arbitrary types, and other useful utilities.

This is the DML counterpart, that enables you to run your tensor computations on DML.
"""

import os
import sys
import platform
import textwrap
import ctypes
import warnings
import torch._C

def is_available() -> bool:
    r"""Returns a bool indicating if DML is currently available."""
    if not hasattr(torch._C, '_dml_getDeviceCount'):
        return False
    # This function never throws and returns 0 if driver is missing or can't
    # be initialized
    return torch._C._dml_getDeviceCount() > 0


def device_count() -> int:
    r"""Returns the number of GPUs available."""
    if is_available():
        return torch._C._dml_getDeviceCount()
    else:
        return 0

def device_name(device_id) -> int:
    r"""Returns the number of GPUs available."""
    if device_id >= 0 and device_id < device_count():
        return torch._C._dml_getDeviceName(device_id)
    else:
        return ""

def default_device() -> int:
    r"""Returns the index of the default selected device."""
    return 0

class DoubleStorage:
    pass


class FloatStorage:
    pass


class HalfStorage:
    pass


class LongStorage:
    pass


class IntStorage:
    pass


class ShortStorage:
    pass


class CharStorage:
    pass


class ULongStorage:
    pass


class UIntStorage:
    pass


class UShortStorage:
    pass


class ByteStorage:
    pass