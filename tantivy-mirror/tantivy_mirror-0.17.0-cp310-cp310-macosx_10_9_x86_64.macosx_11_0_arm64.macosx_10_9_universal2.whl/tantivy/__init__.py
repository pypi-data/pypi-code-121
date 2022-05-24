from .tantivy import *

__doc__ = tantivy.__doc__
if hasattr(tantivy, "__all__"):
    __all__ = tantivy.__all__