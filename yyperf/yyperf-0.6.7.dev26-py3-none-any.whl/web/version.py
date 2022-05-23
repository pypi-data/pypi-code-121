# coding: utf-8
#

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("yyperf").version
except pkg_resources.DistributionNotFound:
    __version__ = "unknown"
