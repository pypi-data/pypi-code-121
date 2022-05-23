#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
RabbitMQ Streams client.
"""

from __future__ import annotations

import asyncio
import contextvars
import enum
import dataclasses as dtc
import inspect
import logging
import os
import platform
import typing as tp
from collections.abc import Awaitable, AsyncIterator, AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from urllib.parse import urlparse

from ..amqp import MessageCtx, get_message_ctx, set_message_ctx
from ..cm import ConnectionManager
from ..types import AMQPBody
from ._client import PublisherConstr, Publisher, Subscriber
from .error import ProtocolError, RbFlyError
from .offset import Offset, OffsetType
from .protocol import RabbitMQStreamsProtocol
from .util import retry, suppress

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')
S = tp.TypeVar('S')
P = tp.ParamSpec('P')

class Scheme(enum.Enum):
    """
    URI schemes for RabbitMQ Streams.
    """
    RABBITMQ_STREAM = 'rabbitmq-stream'
    RABBITMQ_STREAM_TLS = 'rabbitmq-stream+tls'

@dtc.dataclass(frozen=True)
class ConnectionInfo:
    """
    RabbitMQ Streams broker connection information.

    :var scheme: Connection URI scheme.
    :var host: Hostname of RabbitMQ Streams broker.
    :var port: TCP/IP port of RabbitMQ Streams broker.
    :var virtual_host: Virtual host of RabbitMQ Streams broker.
    :var username: RabbitMQ Streams broker authentication username.
    :var password: RabbitMQ Streams broker authentication password.
    """
    scheme: Scheme
    host: str
    port: int
    virtual_host: str
    username: tp.Optional[str]
    password: tp.Optional[str]

    def __str__(self) -> str:
        # NOTE: avoid password
        return '{}://{}@{}:{}/{}'.format(
            self.scheme.value, self.username, self.host, self.port,
            self.virtual_host
        )

class StreamsClient(ConnectionManager[RabbitMQStreamsProtocol]):
    """
    RabbitMQ Streams client.
    """
    def __init__(self, connection_info: ConnectionInfo):
        super().__init__()
        self._cinfo = connection_info

        self._publisher_id = 0
        self._publishers: dict[int, PublisherConstr] = {}

        self._subscription_id = 0
        self._subscribers: dict[int, Subscriber] = {}

    #
    # ConnectionManager abstract methods implementation
    #
    async def _create_protocol(self) -> RabbitMQStreamsProtocol:
        loop = asyncio.get_running_loop()
        cinfo = self._cinfo

        _, proto = await loop.create_connection(
            RabbitMQStreamsProtocol, host=cinfo.host, port=cinfo.port
        )
        logger.info('rabbitmq streams protocol created: {}'.format(cinfo))
        return proto

    async def _connect(self, protocol: RabbitMQStreamsProtocol) -> None:
        """
        Perform connection or reconnection to RabbitMQ Streams broker.

        Recreate existing publishers. See `_read_stream` for subscriber
        recreation.
        """
        cinfo = self._cinfo
        await protocol.connection_handshake(
            cinfo.virtual_host, cinfo.username, cinfo.password
        )
        logger.info('rabbitmq streams client connected: {}'.format(cinfo))

        for publisher in self._publishers.values():
            await self._create_publisher(
                protocol, publisher.stream, publisher.id, publisher.name
            )

        for subscriber in self._subscribers.values():
            msg = subscriber.message
            proto_offset = subscriber.offset if msg is None else Offset.offset(msg.stream_offset + 1)
            await self._subscribe(
                protocol,
                subscriber.stream,
                subscriber.subscription_id,
                proto_offset,
                subscriber.amqp
            )

    async def _disconnect(self, protocol: RabbitMQStreamsProtocol) -> None:
        await protocol.send_close()
        logger.info(
            'rabbitmq streams client disconnected: {}'.format(self._cinfo)
        )

    async def create_stream(self, stream: str) -> None:
        """
        Create RabbitMQ stream.

        Method ignores error received from RabbitMQ Streams broker if the
        stream exists.

        :param stream: RabbitMQ stream name.
        """
        protocol = await self.get_protocol()
        await protocol.create_stream(stream)

    #
    # let's hack API for publisher; the goal is to avoid mixing concepts
    # within single publisher class
    #
    # - send message in AMQP format
    # - send message using opaque binary data - application is responsible
    #   for the format encoding/decoding
    # - send messages in batch mode using above formats
    #
    # therefore, there are 4 ways of sending data and these shall not be
    # mixed, i.e.
    #
    # - `Publisher.batch` enqueues message in batch mode
    # - `Publisher.flush` waits for confirmation of messages sent in batch
    #    mode
    # - if `Publisher.send` is called to send another message, then
    #   - should it wait for confirmation of the single message only?
    #   - should it wait for confirmation of both the message and batched
    #     messages?
    #   - or should an error be raised?
    #
    # let' separate the APIs of publishers to avoid such dilemmas.
    #
    # now, ideally, we want Mypy to accept the following signature
    #
    #     @asynccontextmanager
    #     def publisher(self, stream: str, *, name: str | None=None, cls: type[T]=Publisher) -> AsyncIterator[T]:
    #
    # unfortunately, we need to use the overload hack as suggested at
    #
    #     https://github.com/python/mypy/issues/3737
    #
    @tp.overload
    def publisher(self, stream: str, *, name: str | None=None) -> tp.AsyncContextManager[Publisher]:
        ...

    @tp.overload
    def publisher(self, stream: str, *, name: str | None=None, cls: type[T]) -> tp.AsyncContextManager[T]:
        ...

    @asynccontextmanager
    async def publisher(self, stream, *, name: str | None=None, cls=Publisher):  # type: ignore
        """
        Create publisher for RabbitMQ stream.

        The single message, AMQP publisher is used by default.

        The stream must exist.

        Publisher reference name is used for deduplication of messages. By
        default, the publisher name is ``<hostname>/<pid>``. Override it, if
        this scheme does not work for a specific application, i.e. when
        using threads.

        :param stream: RabbitMQ stream name.
        :param name: RabbitMQ stream publisher reference name.
        :param cls: Publisher class.

        .. seealso::

           - :py:meth:`.StreamsClient.create_stream`
           - :py:class:`rbfly.streams.Publisher`
           - :py:class:`rbfly.streams.PublisherBatch`
        """
        self._publisher_id += 1
        assert 0 < self._publisher_id < 256
        publisher_id = self._publisher_id

        protocol = await self.get_protocol()

        if name is None:
            name = '{}/{}'.format(platform.node(), os.getpid())

        msg_id = await self._create_publisher(
            protocol, stream, publisher_id, name
        )
        pub = cls(self, stream, publisher_id, name, msg_id + 1)
        self._publishers[publisher_id] = pub
        try:
            yield self._publishers[publisher_id]
        finally:
            await self._delete_publisher(publisher_id)

    async def subscribe(
            self,
            stream: str,
            *,
            offset: Offset=Offset.NEXT,
            timeout: float=0,
            amqp: bool=True,
        ) -> tp.AsyncIterator[AMQPBody]:
        """
        Subscribe to the stream and iterate over messages.

        :param stream: Name of RabbitMQ stream to subscribe to.
        :param offset: RabbitMQ Streams offset specification.
        :param timeout: Raise timeout error if no message received within
            specified time (in seconds).
        :param amqp: Messages are in AMQP 1.0 format if true. Otherwise no AMQP decoding.
        """
        self._subscription_id += 1
        sid = self._subscription_id

        protocol = await self.get_protocol()
        proto_offset = await self._get_offset_reference(stream, offset)
        await self._subscribe(protocol, stream, sid, proto_offset, amqp)
        subscriber = Subscriber(self, stream, sid, offset, timeout, amqp)
        self._subscribers[sid] = subscriber

        try:
            async for msg in subscriber:
                set_message_ctx(msg)
                yield msg.body
        finally:
            await self._unsubscribe(stream, sid)

    async def write_offset(
            self, stream: str, reference: str, value: int | None=None
        ) -> None:
        """
        Write RabbitMQ stream offset value using the reference string.

        When offset value is not specified, then the last message context
        is retrieved and its stream offset value is stored. If there is no
        last message context to retrieve, then method does nothing.

        :param stream: Name of RabbitMQ stream.
        :param reference: Offset reference string.
        :param value: Offset value to be stored.
        """
        offset = Offset.reference(reference)
        store_offset = partial(self._store_offset, stream, offset)
        if value is None:
            try:
                ctx = get_message_ctx()
            except LookupError:
                logger.warning(
                    'no context message to store offset value, reference={}'
                    .format(reference)
                )
            else:
                logger.info(
                    'storing offset value of most recent context message,'
                    ' reference={}'.format(reference)
                )
                await store_offset(ctx.stream_offset)
        else:
            await store_offset(value)

    async def _create_publisher(
            self,
            protocol: RabbitMQStreamsProtocol,
            stream: str,
            publisher_id: int,
            name: str,
        ) -> int:
        # TODO: what is the correlation between publisher reference string
        # and publisher id?
        msg_id = await protocol.create_publisher(publisher_id, name, stream)
        logger.info(
            'publisher (re)created, name={}, stream={}, message id={}'
            .format(name, stream, msg_id)
        )
        return msg_id

    async def _subscribe(
        self,
        protocol: RabbitMQStreamsProtocol,
        stream: str,
        subscription_id: int,
        offset: Offset,
        amqp: bool,
    ) -> None:
        """
        Subscribe to RabbitMQ stream.

        :param stream: RabbitMQ stream name.
        :param subscription_id: RabbitMQ stream subscription id.
        :param offset: RabbitMQ Streams offset specification.
        """
        await protocol.subscribe(stream, subscription_id, offset, amqp)
        logger.info(
            '(re)subscribed to stream, name={}, subscription id={},'
            ' offset={}'.format(stream, subscription_id, offset) 
        )

    @suppress(ConnectionError)
    async def _delete_publisher(self, publisher_id: int) -> None:
        """
        Delete RabbitMQ Streams publisher.

        :param publisher_id: Id of publisher to delete.
        """
        try:
            protocol = await self.get_protocol(wait_connected=False)
            await protocol.delete_publisher(publisher_id)
        finally:
            del self._publishers[publisher_id]

    @suppress(ConnectionError)
    async def _unsubscribe(self, stream: str, subscription_id: int) -> None:
        """
        Unsubscribe from a stream.

        :param stream: RabbitMQ stream name.
        :param subscription_id: RabbitMQ stream subscription id.
        """
        protocol = await self.get_protocol(wait_connected=False)
        await protocol.unsubscribe(subscription_id)
        logger.info(
            'unsubscribed from stream, name={}, subscription id={}'
            .format(stream, subscription_id)
        )

    @suppress(ConnectionError)
    async def _store_offset(
        self,
        stream: str,
        offset: Offset,
        last_offset: tp.Optional[int],
    ) -> None:
        """
        Store offset value if offset specification is a reference. 

        :param stream: RabbitMQ stream name.
        :param offset: RabbitMQ Streams offset specification.
        :param last_offset: Offset value to be stored.
        """
        if offset.type == OffsetType.REFERENCE and last_offset is not None:
            assert isinstance(offset.value, str)

            protocol = await self.get_protocol(wait_connected=False)
            protocol.store_offset(stream, offset.value, Offset.offset(last_offset))
            logger.info(
                'stored offset, stream={}, reference={}, offset={}'.format(
                    stream, offset.value, last_offset
                )
            )

    async def _get_offset_reference(self, stream: str, offset: Offset) -> Offset:
        """
        Get RabbitMQ Streams offset specification for stream.

        If offset specification is reference to RabbitMQ Streams offset,
        then query the offset value and return offset specification with
        value increased by 1. Otherwise, return input offset specification.

        :param stream: Name of RabbitMQ stream.
        :param offset: RabbitMQ Streams offset specification.
        """
        if offset.type == OffsetType.REFERENCE:
            assert isinstance(offset.value, str)

            protocol = await self.get_protocol()
            try:
                value = await protocol.query_offset(stream, offset.value)
            except ProtocolError as ex:
                # no offset reference stored, so start with 0
                if ex.code == 0x13:
                    logger.info(
                        'no stream offset reference, stream={}, reference={}'
                        .format(stream, offset.value)
                    )
                    value = 0
            else:
                logger.info(
                    'received stream offset, stream={}, reference={}, offset={}'.format(
                        stream, offset.value, value
                    )
                )
                value += 1

            proto_offset = Offset.offset(value)
        else:
            proto_offset = offset

        return proto_offset

def streams_client(uri: str) -> StreamsClient:
    """
    Create RabbitMQ Streams client using connection URI.

    :param uri: Connection URI.
    """
    p = urlparse(uri)
    port = p.port

    scheme = Scheme(p.scheme)
    host = p.hostname if p.hostname else 'localhost'
    vhost = p.path if p.path else '/'

    if port is None and scheme == Scheme.RABBITMQ_STREAM:
        port = 5552
    elif port is None and scheme == Scheme.RABBITMQ_STREAM_TLS:
        port = 5551
    elif port is None:
        port = 5552

    conn_info = ConnectionInfo(scheme, host, port, vhost, p.username, p.password)
    return StreamsClient(conn_info)

@tp.overload
def connection(
        f: tp.Callable[P, Awaitable[T]]
    ) -> tp.Callable[P, Awaitable[T]]:
    ...

@tp.overload
def connection(
        f: tp.Callable[P, AsyncGenerator[T, S]]
    ) -> tp.Callable[P, AsyncGenerator[T, S]]:
    ...

def connection(
        f: tp.Callable[P, Awaitable[T]] | tp.Callable[P, AsyncGenerator[T, S]]
    ) -> tp.Callable[P, Awaitable[T]] | tp.Callable[P, AsyncGenerator[T, S]]:
    """
    Decorator to manage RabbitMQ Streams client connection.

    Streams client implements connection manager abstract class.

    Streams client has to be the first parameter of coroutine `f`. On exit
    the streams client is disconnected using connection manager API.

    :param f: Coroutine using RabbitMQ Streams client.
    """
    f_coro = tp.cast(tp.Callable[P, Awaitable[T]], f)
    f_gen = tp.cast(tp.Callable[P, AsyncGenerator[T, S]], f)
    async def wrapper(*args: P.args, **kw: P.kwargs) -> T:
        try:
            client = tp.cast(
                ConnectionManager[RabbitMQStreamsProtocol], args[0]  # type: ignore
            )
            result = await f_coro(*args, **kw)
        finally:
            await client.disconnect()
        return result

    async def wrapper_gen(*args: P.args, **kw: P.kwargs) -> AsyncGenerator[T, S]:
        try:
            client = tp.cast(
                ConnectionManager[RabbitMQStreamsProtocol], args[0]  # type: ignore
            )
            async for v in f_gen(*args, **kw):
                yield v
        finally:
            await client.disconnect()

    if inspect.iscoroutinefunction(f):
        return wrapper
    elif inspect.isasyncgenfunction(f):
        return wrapper_gen
    else:
        raise RbFlyError(
            'Asynchronous coroutine or generator function required'
        )

# vim: sw=4:et:ai
