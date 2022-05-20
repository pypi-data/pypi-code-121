import sys
from pathlib import Path
"""Top-level package for Lock My Resource."""

lockmyresource_path = Path(__file__).parent
assert isinstance(lockmyresource_path, Path)
sys.path.insert(0, str(lockmyresource_path.absolute()))
from metainfo import author, email, version

__author__ = author
__email__ = email
__version__ = version
