from types import ModuleType
from typing import Union

from thriftpy2.contrib.aio.protocol import (
    TAsyncProtocolBase,
    TAsyncBinaryProtocolFactory,
)
from thriftpy2.contrib.aio.transport import (
    TAsyncTransportBase,
    TAsyncBufferedTransportFactory,
)
from thriftpy2.contrib.aio.client import TAsyncClient

import httpx

from .transport import TAsyncHTTPXClient

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class TProtocolFactory(Protocol):
    def get_protocol(self, trans: TAsyncTransportBase) -> TAsyncProtocolBase:
        ...


class TTransportFactory(Protocol):
    def get_transport(self, trans: TAsyncTransportBase) -> TAsyncTransportBase:
        ...


async def make_client(
    service: ModuleType,
    host: str = 'localhost',
    port: int = 9090,
    url: Union[str, httpx.URL] = None,
    proto_factory: TProtocolFactory = TAsyncBinaryProtocolFactory(),
    trans_factory: TTransportFactory = TAsyncBufferedTransportFactory(),
    **kwargs,
) -> TAsyncClient:
    """
    Create a Thrift client for the given service and transport/protocol
    configuration. Analogous to the socket implementation:
    :py:func:`thriftpy2.contrib.aio.rpc.make_client`

    :param service:
        Thrift service (generated module from a .thrift file) to create
        the Thrift client for.
    :param host: Thrift HTTP server hostname
    :param port: Thrift HTTP server port
    :param url: Thrift server URL. Takes precedence over host and port
    :param proto_factory:
        Protocol factory for creating :py:class:`TAsyncProtocolBase` instances.
        Must have a ``get_protocol(transport)`` method.
    :param trans_factory:
        Transport factory for creating :py:class:`TAsyncTransportBase`
        instances. Must have a ``get_transport(transport)`` method.
    :param kwargs:
        Extra keyword arguments to pass to :py:class:`TAsyncHTTPXClient`
        which will be passed onto :py:class:`httpx.AsyncClient`
    :return: Newly initialized :py:class:`TAsyncClient` instance.
    """
    url = url if url else f'http://{host}:{port}/'
    client = TAsyncHTTPXClient(url, **kwargs)
    transport = trans_factory.get_transport(client)
    protocol = proto_factory.get_protocol(transport)
    await transport.open()
    return TAsyncClient(service, protocol)
