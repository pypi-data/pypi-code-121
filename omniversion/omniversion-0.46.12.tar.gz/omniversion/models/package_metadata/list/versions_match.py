"""List of installations of one particular package"""
from collections import UserList
from typing import Optional, List, Set

from ..package_metadata import PackageMetadata


class VersionsMatch(UserList):
    """List of installations of one particular package"""
    display_name: str
    """The name to display to the user."""
    expected_num: Optional[int]
    """The number of packages expected to be found. This prevents false positives where versions appear to match \
    due to some versions not being fetched."""

    def __init__(
            self,
            data: List[PackageMetadata],
            display_name: Optional[str] = None,
            expected_num: Optional[int] = None,
    ):
        """Initialize the dependency match"""
        super().__init__(data)
        self.display_name = display_name
        self.expected_num = expected_num

    @property
    def is_consistent(self) -> bool:
        """Do all versions match?"""
        if len(self.deduplicated_versions) == 1:
            return True
        return False

    @property
    def has_all_expected_items(self) -> bool:
        """Does the number of dependencies match the expected value?"""
        return self.expected_num is None or len(self.data) == self.expected_num

    @property
    def versions(self) -> List[str]:
        """All dependency versions with duplicates removed"""
        return [dependency.current for dependency in self.data if dependency.current is not None]

    @property
    def deduplicated_versions(self) -> Set[str]:
        """All dependency versions with duplicates removed"""
        return {dependency.current for dependency in self.data}

    def __repr__(self) -> str:
        if len(self.versions) == 0:
            return f"No `{self.display_name}` versions found"
        if len(self.versions) == 1:
            return f"Only one `{self.display_name}` version found"
        suffix = ""
        if not self.has_all_expected_items:
            suffix = f" (only {len(self.versions)} of {self.expected_num} found)"
        if self.is_consistent:
            return f"Versions match for package `{self.display_name}`: {', '.join(self.versions)}{suffix}"
        return f"Versions mismatch for package `{self.display_name}`: {', '.join(self.versions)}{suffix}"
