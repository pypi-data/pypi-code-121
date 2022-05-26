"""The fw_gear_splitter package."""
from importlib import metadata

pkg_name = __package__
try:
    __version__ = metadata.version(__package__)
except:  # pragma: no cover
    __version__ = "0.1.0"
