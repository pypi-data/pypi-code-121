from importlib_metadata import version

# catching any exception to make sure
# the `import mlfoundry` code does not fail
# if `version` function fails for some reason
try:
    __version__ = version("mlfoundry")
except Exception:
    __version__ = None
