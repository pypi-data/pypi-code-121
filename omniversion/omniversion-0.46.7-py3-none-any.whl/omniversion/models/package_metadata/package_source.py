"""Model class representing a source of a particular package, typically a remote repository"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PackageSource:
    """A repository or other source from which a package may be obtained."""
    identifier: Optional[str] = None
    """The identifier used to refer to this source."""
    url: Optional[str] = None
    """A url from which the package can be loaded, if any."""
    versions: Optional[List[str]] = None
    """All versions of the package known to be available from this source."""
