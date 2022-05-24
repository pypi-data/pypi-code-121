__all__ = [
    'make_aio_client',
    'make_sync_client',
    'TAsyncHTTPXClient',
    'THTTPXClient',
]

from .aio import TAsyncHTTPXClient, make_client as make_aio_client
from .sync import THTTPXClient, make_client as make_sync_client

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
