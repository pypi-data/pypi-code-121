"""Root module. Starting point for loading and using omniversion data."""
from typing import List, Optional

from omniversion.models import PackagesMetadataList, Localhost, Host
from omniversion.models.data_source.data_sources import DataSources


class Omniversion:
    """The `omniversion.Omniversion` class used to load and handle all omniversion data.

    You will probably want to use an `omniversion/ansible` role first. It will fetch package metadata
    from remote hosts, saving it to local `.omniversion.yaml` files.

    Parameters
    ----------
    base_path
        The absolute or relative path to the folder containing the `.omniversion.yaml` files. If `None` is \
    specified, the default value of `/tmp/omniversion` (matching the `omniversion/ansible` roles' default output \
    directory) will be used. The expected folder structure is \
    `base_path` / `hostname` / `package_manager` / `verb`.omniversion.yaml, \
    which is the structure emitted by the `omniversion/ansible` roles.

    data_sources
        Optional data sources to include in addition to the data found in the specified `base_path`. \
    You won't normally need this.
    """

    def __init__(self, base_path: Optional[str] = "/tmp/omniversion", data_sources: Optional[DataSources] = None):
        self.sources = data_sources if data_sources is not None else DataSources()
        if base_path is not None:
            self.sources.add_files(base_path=base_path)

    @property
    def packages(self) -> PackagesMetadataList:
        """List of all package metadata items that have been loaded."""
        return PackagesMetadataList(self.sources.packages)

    @property
    def hostnames(self) -> List[str]:
        """Names of hosts from which data has been loaded."""
        return self.sources.hostnames

    @property
    def hosts(self) -> List[Host]:
        """List of hosts from which data has been loaded."""
        return Host.list_from_packages(self.packages)

    @property
    def localhost(self) -> Localhost:
        """Convenience property to access the localhost."""
        return Localhost(PackagesMetadataList(self.packages.filter(host="localhost")))

    def __str__(self):
        """Debug string representation describing the loaded data.

        Use the `omniversion.pretty_print` module for prettier output more suitable for human consumption."""
        return f"omniversion data: {self.sources}"
