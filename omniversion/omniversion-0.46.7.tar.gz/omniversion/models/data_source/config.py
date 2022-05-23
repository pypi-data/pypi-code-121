"""Package info obtained from a configuration file.

Some package versions are specified in local files (e.g. a configuration file, an environment file, a Dockerfile,
or an Ansible playbook with a hardcoded version). You can extract them using regular expressions.
A ConfigDataSource tracks the metadata related to this process."""
import os
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple

from ...models.package_metadata.package_metadata import PackageMetadata


@dataclass
class ConfigDataSource:
    """Package info obtained from a configuration file.

    Some package versions are specified in local files (e.g. a configuration file, an environment file, a Dockerfile,
    or an Ansible playbook with a hardcoded version). You can extract them using regular expressions.
    A ConfigDataSource tracks the metadata related to this process."""
    file_path: str
    """The path of the configuration or environment file that specifies one or more package version(s)."""
    regex: str
    """A Python-flavor regular expression used to extract the version(s) from the file. It should contain a group
    called `version` and, unless the `name` property is specified, a named group called `name`."""
    name: Optional[str] = None
    """The name of the package. This is required if the regex does not contain a `name` group."""
    num_packages: Optional[int] = None
    """After extraction, this value specifies the number of extracted versions."""
    host: Optional[str] = None
    """The host is given only for future compatibility. Currently, the only valid value is `localhost`."""

    @classmethod
    def load(cls, file_path: str, regex: str, name: Optional[str] = None) -> \
            Tuple['ConfigDataSource', List[PackageMetadata]]:
        """Load package info from a local file

        Parameters
        ----------
        file_path
            A relative or absolute path to a file.
        regex
            A Python-flavor regular expression used to extract the version(s) from the file.
        name
            The name of the package. This is required if the regex does not contain a `name` group.

        Returns
        -------
        Tuple[ConfigDataSource, List[omniversion.models.package_metadata.package_metadata.PackageMetadata]]
            A `ConfigDataSource` object containing extraction metadata and extracted package info as a list of \
            `omniversion.models.package_metadata.package_metadata.PackageMetadata` objects.
        """
        real_file_path = os.path.realpath(file_path)
        with open(real_file_path, encoding="utf8") as file:
            try:
                matches = re.compile(regex).finditer(file.read())
                package_name = name
                packages = []
                for match in matches:
                    version = match.group("version")
                    if package_name is None:
                        package_name = match.group("name")
                    package_metadata = PackageMetadata(
                        host="localhost",
                        name=package_name,
                        package_manager="file",
                        current=version,
                    )
                    packages += [package_metadata]
                config_data_source = ConfigDataSource(
                    num_packages=len(packages),
                    host="localhost",
                    file_path=file_path,
                    regex=regex,
                    name=name,
                )
                return config_data_source, packages
            except IndexError as exception:
                raise IndexError("Invalid regex. You need to provide a named group called `version` and either a name "
                                 "parameter or a named group called `name`") from exception

    def __str__(self):
        def entries_text():
            if self.num_packages == 0:
                return "No packages"
            if self.num_packages == 1:
                return "1 package"
            return f"{self.num_packages} packages"
        return f"{entries_text()} found in config"
