"""An imported file including meta data"""
import os
import time
from dataclasses import dataclass
from typing import Optional, List, Any, Tuple

import yaml
from dacite import from_dict, ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError

from ..package_metadata.package_metadata import PackageMetadata

STALENESS_THRESHOLD_IN_SECS: int = 60 * 60

AVAILABLE_VERBS = ["audit", "list", "refresh", "outdated", "version"]


@dataclass
class FileDataSource:
    """An imported file including meta data"""
    num_packages: Optional[int] = None
    """The number of package metadata items that have been imported."""
    verb: Optional[str] = None
    """The type of package manager command used to create the data in this file (e.g. `list`, `audit`, etc.)."""
    host: Optional[str] = None
    """The host from which the data was extracted."""
    package_manager: Optional[str] = None
    """The identifier of the package manager through which the data was obtained."""
    version: Optional[str] = None
    """The version of the `omniversion/cli` executable used to create the file."""
    timestamp: Optional[float] = None
    """The time the file was last changed. Used to determine if data is stale and should be re-fetched."""
    path: Optional[str] = None
    """The absolute or relative path to the file."""

    @property
    def is_stale(self):
        """Data that was fetched a long time ago is considered stale"""
        return self.timestamp is None or time.time() > STALENESS_THRESHOLD_IN_SECS + self.timestamp

    @property
    def has_data(self):
        """Does the file contain any parseable data at all?"""
        return self.num_packages is not None and self.num_packages > 0

    @classmethod
    def load_data(cls, file_path: str, verb: str, host: str, package_manager: str) -> \
            Tuple[Optional['FileDataSource'], List[PackageMetadata]]:
        """Load data from the specified file.

        Parameters
        ----------
        file_path
            The relative or absolute path to the file.
        verb
            The type of package manager command used to create the data in this file (e.g. `list`, `audit`, etc.).
        host
            The host from which the data was extracted.
        package_manager
            The identifier of the package manager through which the data was obtained.

        Returns
        -------
        Tuple[FileDataSource, List[omniversion.models.package_metadata.package_metadata.PackageMetadata]]
            A `FileDataSource` object containing extraction metadata and extracted package info as a list of \
            `omniversion.models.package_metadata.package_metadata.PackageMetadata` objects.
        """
        if not os.path.exists(file_path):
            return None, []
        version, packages_data, timestamp = cls._extract_yaml_data(file_path)
        if packages_data is None:
            return FileDataSource(
                num_packages=None, version=version, host=host, package_manager=package_manager,
                verb=verb, timestamp=timestamp, path=file_path
            ), []
        packages: List[PackageMetadata] = [cls._parse_package_data(package_data) for package_data in packages_data]
        # remove packages that didn't parse correctly
        packages = [package for package in packages if package is not None]
        for package in packages:
            package.verb = verb
            package.host = host
            package.package_manager = package_manager
        return FileDataSource(
            num_packages=len(packages),
            version=version,
            host=host,
            package_manager=package_manager,
            verb=verb,
            timestamp=timestamp,
            path=file_path,
        ), packages

    @classmethod
    def _parse_package_data(cls, data: Any) -> Optional[PackageMetadata]:
        try:
            return from_dict(data_class=PackageMetadata, data=data)
        except (ForwardReferenceError, KeyError, MissingValueError, TypeError, UnexpectedDataError, WrongTypeError):
            # TODO: log this (!)
            return None

    @classmethod
    def _extract_yaml_data(cls, file_path: str) -> Tuple[Optional[str], Optional[list[any]], Optional[float]]:
        """load an omniversion file containing yaml data"""
        timestamp = None
        try:
            timestamp = os.stat(file_path).st_ctime
            with open(file_path, encoding="utf8") as file:
                # a yaml file may contain multiple documents
                # we want to extract all
                documents = yaml.safe_load_all(file)
                # the version of omniversion
                version = None
                items = []
                for document in documents:
                    if document is None:
                        continue
                    # we assume that all documents within the same file were written by the same omniversion version
                    if version is None and "version" in document:
                        version = document["version"]
                    if "items" in document:
                        items += document["items"]
                return version, items, timestamp
        except (TypeError, yaml.YAMLError):
            # TODO: log this (!)
            return None, None, timestamp

    def __str__(self):
        if self.num_packages is None:
            return f"No valid `{self.verb}` data loaded for `{self.package_manager}`"
        data_recency = "Stale" if self.is_stale else "Recent"
        if self.num_packages == 1:
            return f"{data_recency} `{self.verb}` data loaded for `{self.package_manager}` (1 package)`"
        if self.num_packages > 1:
            return f"{data_recency} `{self.verb}` data loaded for `{self.package_manager}`" \
                   f" ({self.num_packages} packages)"
        return f"No `{self.verb}` data loaded for `{self.package_manager}`"
