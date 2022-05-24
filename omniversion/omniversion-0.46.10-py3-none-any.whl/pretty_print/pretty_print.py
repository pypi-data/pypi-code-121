"""Pretty-print some data as a human-readable string"""
from pprint import PrettyPrinter
from typing import Tuple

from omniversion import Omniversion
from omniversion.models import DataSources, Host, FileDataSource, ConfigDataSource, PackagesMetadataList, \
    AvailableUpdates, Vulnerabilities, VersionsMatch
from omniversion.pretty_print.data_source import _pretty_print_data_source
from omniversion.pretty_print.host import _pretty_print_host
from omniversion.pretty_print.omniversion import _pretty_print_omniversion
from omniversion.pretty_print.package_metadata import _pretty_print_package_metadata_list


class OmniversionPrettyPrinter(PrettyPrinter):
    """`PrettyPrinter` subclass that knows how to format `omniversion` objects"""

    def format(self, obj: object,  # pylint: disable=arguments-renamed
               context, maxlevels: int, level: int) -> Tuple[str, bool, bool]:
        def recursive_format(value: object) -> str:
            return self.format(value, context=context, maxlevels=maxlevels, level=level - 1)[0]

        if isinstance(obj, Host):
            return _pretty_print_host(obj), False, False

        if isinstance(obj, (PackagesMetadataList, AvailableUpdates, VersionsMatch, Vulnerabilities)):
            return _pretty_print_package_metadata_list(obj), False, False

        if isinstance(obj, (DataSources, ConfigDataSource, FileDataSource)):
            return _pretty_print_data_source(obj, recursive_format), False, False

        if isinstance(obj, Omniversion):
            return _pretty_print_omniversion(obj, recursive_format), False, False

        return super().format(obj, context, maxlevels, level)


def pprint(obj: object, indent=1, width=80, depth=None, compact=False,  # pylint: disable=too-many-arguments
           stream=None):
    """Pretty-print an object to stdout (or the provided stream)"""
    OmniversionPrettyPrinter(indent=indent, width=width, depth=depth, compact=compact, stream=stream) \
        .pprint(obj)


def pformat(obj: object, indent=1, width=80, depth=None, compact=False) -> str:
    """Return a pretty-printed representation of the passed"""
    return OmniversionPrettyPrinter(indent=indent, width=width, depth=depth, compact=compact).pformat(obj)
