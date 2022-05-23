from .base import (
    BaseRequest,
    Response,
    HTTPRequestMethod,
    IRequestPostCondition,
)

try:
    from .aiohttp_conn import Request
except ImportError:
    pass

try:
    from .requests_conn import Request
except ImportError:
    pass

__all__ = (
    "BaseRequest",
    "IRequestPostCondition",
    "Response",
    "HTTPRequestMethod",
)
