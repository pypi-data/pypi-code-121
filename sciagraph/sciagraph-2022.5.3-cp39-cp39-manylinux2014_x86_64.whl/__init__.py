"""
Sciagraph, the production memory profiler for scientists and data scientists.

This is proprietary software.
"""
try:
    from importlib.metadata import version  # type: ignore
except ImportError:
    from importlib_metadata import version  # type: ignore

__version__ = version("sciagraph")
del version
