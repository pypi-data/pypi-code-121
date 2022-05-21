from .wasmer import *

__doc__ = wasmer.__doc__
if hasattr(wasmer, "__all__"):
    __all__ = wasmer.__all__