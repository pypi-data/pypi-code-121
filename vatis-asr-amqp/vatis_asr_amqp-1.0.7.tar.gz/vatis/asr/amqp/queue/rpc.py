import time
import uuid
from concurrent.futures import Future
from typing import Optional, Dict, Any

from . import constants
from .model import Queue, DEFAULT_EXCHANGE
from .routing import Route
from .connection import ConnectionFactory
from .consumer import ConsumerManager, Consumer, RpcConsumer
from .headers import CORRELATION_ID_HEADER, TIMEOUT_HEADER, REQUEST_TIMESTAMP_HEADER

from vatis.asr_commons.config.logging import get_logger

logger = get_logger(__name__)


class TimeoutFuture(Future):
    def __init__(self, timeout: Optional[float] = None):
        super().__init__()
        self._created_time: float = time.time()
        self._timeout: Optional[float] = timeout

    def result(self, **kwargs):
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = self._timeout

            if timeout is not None:
                timeout -= time.time() - self._created_time

        return super().result(timeout)

    def exception(self, **kwargs):
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = self._timeout

            if timeout is not None:
                timeout -= time.time() - self._created_time

        return super().exception(timeout)

    @property
    def timed_out(self) -> bool:
        return time.time() - self._created_time > self._timeout


class RpcManager(ConsumerManager):
    def __init__(self, connection_factory: ConnectionFactory,
                 prefetch_count: int = 1,
                 global_prefetch: bool = False):
        super().__init__(connection_factory,
                         prefetch_count=prefetch_count,
                         global_prefetch=global_prefetch)
        self._rpc_response_queue: Queue = Queue(name=f'rpc-{uuid.uuid4()}',
                                                auto_delete=True,
                                                exclusive=True)
        self._rpc_requests: Dict[str, TimeoutFuture] = {}

        def _dispatch_rpc_response(response, headers: Dict[str, str]) -> bool:
            if CORRELATION_ID_HEADER in headers and headers[CORRELATION_ID_HEADER] in self._rpc_requests:
                correlation_id: str = headers[CORRELATION_ID_HEADER]
                future: TimeoutFuture = self._rpc_requests[correlation_id]

                if not future.timed_out:
                    if isinstance(response, Exception):
                        future.set_exception(response)
                    else:
                        future.set_result(response)
                else:
                    logger.warning(f'Response for request {correlation_id} timed out')

                self._rpc_requests.pop(correlation_id)

            return True

        consumer: Consumer = Consumer(queue=self._rpc_response_queue,
                                      exchange=DEFAULT_EXCHANGE,
                                      dtype=None,
                                      callback=_dispatch_rpc_response)

        super().add_consumer(consumer=consumer)

    def rpc_call(self, route: Route,
                 message: Any,
                 timeout: Optional[float] = None,
                 headers: Dict[str, str] = None,
                 delivery_mode: int = constants.DELIVERY_MODE_PERSISTENT) -> Future:
        from .publisher import publisher

        self._cleanup_timed_out_requests()

        if headers is None:
            headers = {}

        ttl_millis: Optional[float] = None

        if timeout is not None:
            headers[TIMEOUT_HEADER] = str(timeout)
            headers[REQUEST_TIMESTAMP_HEADER] = str(time.time())
            ttl_millis = int(timeout * 1000)

        correlation_id: str = str(uuid.uuid4())
        future: TimeoutFuture = TimeoutFuture(timeout=timeout)

        self._rpc_requests[correlation_id] = future

        publisher.push_to_routes(message=message,
                                 routes=[route],
                                 ttl_millis=ttl_millis,
                                 headers=headers,
                                 delivery_mode=delivery_mode,
                                 reply_to=self._rpc_response_queue.name,
                                 correlation_id=correlation_id)

        return future

    def _cleanup_timed_out_requests(self):
        self._rpc_requests = {correlation_id: future for correlation_id, future in self._rpc_requests.items() if not future.timed_out}

    def add_consumer(self, consumer: RpcConsumer):
        super().add_consumer(consumer)


rpc_manager: Optional[RpcManager] = None


def __init__(connection_factory: ConnectionFactory,
             prefetch_count: int = 1,
             global_prefetch: bool = False):
    global rpc_manager

    rpc_manager = RpcManager(connection_factory=connection_factory,
                             prefetch_count=prefetch_count,
                             global_prefetch=global_prefetch)

