from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("linkhub_prometheus_exporter")
except PackageNotFoundError:
    # This package is not installed.
    __version__ = "unknown"
finally:
    del PackageNotFoundError, version
