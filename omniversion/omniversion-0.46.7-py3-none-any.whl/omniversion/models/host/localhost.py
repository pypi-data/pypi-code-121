"""A special `omniversion.models.host.host.Host` object denoting the machine on which the `omniversion` Python module \
is being run."""
from .host import Host
from ..package_metadata.list.packages_metadata_list import PackagesMetadataList


class Localhost(Host):
    """A special `omniversion.models.host.host.Host` object denoting the machine on which the `omniversion` Python \
    module is being run."""
    def __init__(self, packages: PackagesMetadataList):
        super().__init__("localhost", packages)

    def __str__(self):
        return "localhost"
