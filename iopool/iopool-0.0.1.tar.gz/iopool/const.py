from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin


if TYPE_CHECKING:
    from typing import Mapping



API_URL = 'https://api.iopool.com/v1'
"""IOPool API root URL"""


class ROUTES:
    """Store routes"""
    POOLS = '/pools'
    """List managed pools"""

    POOL = '/pools/{pool_id}'
    """Get a single pool"""

    names: Mapping[str, str] = dict(
        pools=POOLS,
        pool=POOL,
    )

    @classmethod
    def url_for(cls, route: str, **kwargs) -> str:
        """
        Generate a URL for a route.

        :param route: Route name
        :param kwargs: Route parameters
        :return: URL
        """
        return urljoin(API_URL, cls.names[route].format(**kwargs))
