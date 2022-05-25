"""Top-level module for describe-get-system proof of concept.

- allow end-user to describe his or her requirement to build test script.
"""

from dgspoc.core import Dgs
from dgspoc.core import sleep
from dgspoc.core import wait_for
from dgspoc.core import connect_device
from dgspoc.core import disconnect_device
from dgspoc.core import release_device
from dgspoc.core import destroy_device
from dgspoc.core import execute
from dgspoc.core import configure
from dgspoc.core import reload
from dgspoc.core import convert_and_filter

from dgspoc.config import version

__version__ = version

__all__ = sorted([
    'Dgs',
    'wait_for',
    'sleep',
    'connect_device',
    'disconnect_device',
    'release_device',
    'destroy_device',
    'execute',
    'configure',
    'reload',
    'convert_and_filter',
    'version',
])
