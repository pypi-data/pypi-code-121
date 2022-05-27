from typing import TYPE_CHECKING

from . import core
from .core import LazyModule

if TYPE_CHECKING:
    from . import jax
    from . import torch
    from . import univ
else:
    jax   = LazyModule("nxml.jax")
    torch = LazyModule("nxml.torch")
    univ  = LazyModule("nxml.univ")


__all__ = [
    "core",
    "jax",
    "torch",
    "univ",
]

__version__ = "0.0.1.dev1"
