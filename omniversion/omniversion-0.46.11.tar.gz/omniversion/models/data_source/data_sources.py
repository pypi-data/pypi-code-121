"""Model class for metadata regarding the package info available to `omniversion`."""
import os
from typing import List, Optional, Tuple

from .config import ConfigDataSource
from .file import FileDataSource
from ..package_metadata.package_metadata import PackageMetadata

VALID_VERBS = ["audit", "list", "refresh", "outdated", "version"]


class DataSources:
    """Metadata regarding the package info available to `omniversion`.

    `omniversion.models.package_metadata.package_metadata.PackageMetadata` contains metadata on packages, `DataSources`
    contains "meta-metadata" about what kind of package information is available and how it was obtained."""
    def __init__(self, files: Optional[List[FileDataSource]] = None, configs: Optional[List[ConfigDataSource]] = None,
                 packages: Optional[List[PackageMetadata]] = None) -> None:
        """Create a new data sources object, loading the specified files and configuration values.

        Parameters
        ----------
        files
            Optional list of `.omniverison.yaml` files from which package info will be loaded.
        configs
            Optional list of configuration files from which package info will be extracted.
        packages
            Additional packages to be included in addition to the loaded packages. These will have no \
        associated file.
        """
        self.packages = packages if packages is not None else []
        self.files = []
        if files is not None:
            for file in files:
                self.add_file(file_path=file.path, verb=file.verb, host=file.host, package_manager=file.package_manager)
        self.configs = []
        if configs is not None:
            for config in configs:
                self.add_config(file_path=config.file_path, regex=config.regex, name=config.name)

    def add_files(self, base_path: str) -> List[PackageMetadata]:
        """Load package info from a folder on the local machine.

        Parameters
        ----------
        base_path
            The base from which to load the files. The expected folder structure is
        `base_path` / `hostname` / `package_manager` / `verb`.omniversion.yaml,
        which is the structure emitted by the omniversion/ansible roles.

        Returns
        -------
        List
            A list of extracted package metadata is returned for convenience. The same data is also added
        to the `packages` property of the `DataSources` object."""
        files = []
        packages = []
        real_path = os.path.realpath(base_path)
        host_dirs = sorted([
            directory
            for directory in os.listdir(real_path)
            if os.path.isdir(os.path.join(real_path, directory))
        ])
        for host in host_dirs:
            host_path = os.path.join(real_path, host)
            package_manager_dirs = sorted([
                directory
                for directory in os.listdir(host_path)
                if os.path.isdir(os.path.join(host_path, directory))
            ])
            for package_manager in package_manager_dirs:
                for verb in VALID_VERBS:
                    file_path = os.path.join(host_path, package_manager, verb + ".omniversion.yaml")
                    file, new_packages = FileDataSource.load_data(file_path, verb, host, package_manager)
                    if file:
                        files.append(file)
                    if new_packages:
                        packages += new_packages
        self.files.extend(files)
        self.packages.extend(packages)
        return packages

    def add_file(self, file_path: str, verb: str, host: str, package_manager: str) -> List[PackageMetadata]:
        """Add package info from a single `.omniversion.yaml` file.

        Parameters
        ----------
        file_path
            The relative or absolute path of the file to load. It is not required to have any particular structure.
        verb
            The verb, i.e. package manager command type, used to extract this package info (e.g. `list`/`audit`).
        host
            The name of the host from which the data was extracted.
        package_manager
            The identifier of the package manager from which the package info was obtained.

        Returns
        -------
        List[omniversion.models.package_metadata.package_metadata.PackageMetadata]
            A list of extracted package metadata for convenience. The same data is also added to the `packages`
        property of the `DataSources` object.
        """
        file, packages = FileDataSource.load_data(file_path, verb, host, package_manager)
        if file:
            self.files.append(file)
        self.packages.extend(packages)
        return packages

    def add_config(self, file_path: str, regex: str, name: Optional[str] = None) -> List[PackageMetadata]:
        """Add package info from a configuration file in arbitrary format.

        Parameters
        ----------
        file_path
            The relative or absolute path of the file to load. It is not required to have any particular structure.
        regex
            A Python-flavor regular expression used to extract the version(s) from the file.
        name
            The name of the package. This is required if the regex does not contain a `name` group.

        Returns
        -------
        List[DataSources]
            A list of extracted package metadata for convenience. The same data is also added to the `packages` \
        property of the `DataSources` object.
        """
        config, packages = ConfigDataSource.load(file_path, regex, name)
        self.configs.append(config)
        self.packages.extend(packages)
        return packages

    @property
    def hostnames(self) -> List[str]:
        """Deduplicated list of hosts for which files are present in the list"""
        return sorted(list({file.host for file in self.files}))

    @property
    def host_infos(self) -> List[Tuple[str, List[FileDataSource], List[ConfigDataSource]]]:
        """List of host information, containing the hostname, a list of `.omniversion.yaml` files and a list of
        configuration files from which packages have been loaded.
        """
        def item_for_host(hostname: str):
            sources_for_host = self.for_host(hostname=hostname)
            return hostname, sources_for_host.files, sources_for_host.configs
        return [item_for_host(hostname) for hostname in self.hostnames]

    @property
    def package_manager_identifiers(self) -> List[str]:
        """Deduplicated list of hosts for which files are present in the list."""
        return sorted(list({file.package_manager for file in self.files}))

    def for_host(self, hostname: str) -> 'DataSources':
        files = [file for file in self.files if file.host == hostname]
        configs = [config for config in self.configs if config.host == hostname]
        return DataSources(files=files, configs=configs)

    def __len__(self) -> int:
        return len(self.files) + len(self.configs)

    def __str__(self):
        num_files = len(self.files)
        num_configs = len(self.configs)
        num_hosts = len(self.hostnames)
        files_desc = f"{num_files} file{'s' if num_files != 1 else ''}"
        configs_desc = f"{num_configs} config item{'s' if num_configs != 1 else ''}"
        hosts_desc = f"{num_hosts} host{'s' if num_hosts != 1 else ''}"
        if num_files + num_configs == 0:
            return "no sources loaded"
        return f"{files_desc} and {configs_desc} loaded for {hosts_desc}"
