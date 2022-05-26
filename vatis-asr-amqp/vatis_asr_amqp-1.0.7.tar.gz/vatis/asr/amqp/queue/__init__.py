from concurrent.futures import Future
from typing import Optional, Type, Dict, Tuple, List, Any

from vatis.asr_commons.config.logging import get_logger

from . import environment, rpc
from . import routing
from .connection import ReconnectingAMQPConnection, ConnectionState
from .constants import *
from .consumer import ConsumerManager, Consumer, RpcConsumer
from .exceptions import ConnectionClosedException, NoRouteFoundException, RetriesExceededException
from .model import DEFAULT_EXCHANGE, Queue, Exchange, TRANSCRIPTION_RESULT_WAITING_EXCHANGE
from .publisher import Publisher
from .routing import RoutingRule, Route
from . import consumer
from . import headers

logger = get_logger(__name__)
_initialized = False
_consumers_enabled = True


def __init__(enable_consumers: bool = True,
             prefetch_count: int = 1,
             global_prefetch: bool = False,
             rpc_prefetch_count: int = 1,
             rpc_global_prefetch: bool = False):
    """
    Initialize queue module
    :param enable_consumers: register consumers
    :param prefetch_count: maximum unacknowledged messages per channel
    :param global_prefetch: set prefetch limit on connection instead of channel
    :param rpc_prefetch_count: maximum unacknowledged messages per channel for rpc connection
    :param rpc_global_prefetch: set prefetch limit on connection instead of channel for rpc connection
    :return:
    """
    global _initialized
    global _consumers_enabled

    if _initialized:
        return

    from . import connection

    connection.__init__()

    from .connection import connection_factory

    initialization_connection: ReconnectingAMQPConnection = connection_factory.create()
    try:
        _declare_dead_letter_exchange(initialization_connection)
        _declare_waiting_transcription_result_exchange(initialization_connection)
    finally:
        initialization_connection.close()

    routing.__init__()
    if enable_consumers:
        consumer.__init__(connection_factory,
                          prefetch_count=prefetch_count,
                          global_prefetch=global_prefetch)
        rpc.__init__(connection_factory,
                     prefetch_count=rpc_prefetch_count,
                     global_prefetch=rpc_global_prefetch)

    publisher.__init__(connection_factory)

    _initialized = True
    _consumers_enabled = True


def _declare_dead_letter_exchange(connection: ReconnectingAMQPConnection):
    with connection.channel() as channel:
        channel.exchange_declare(exchange=DEAD_LETTER_EXCHANGE_NAME,
                                 exchange_type=DEAD_LETTER_EXCHANGE_TYPE.value)

        channel.queue_declare(queue=DEAD_LETTER_QUEUE_NAME,
                              durable=True)

        channel.queue_bind(queue=DEAD_LETTER_QUEUE_NAME,
                           exchange=DEAD_LETTER_EXCHANGE_NAME,
                           routing_key=DEAD_LETTER_QUEUE_NAME)


def _declare_waiting_transcription_result_exchange(connection: ReconnectingAMQPConnection):
    with connection.channel() as channel:
        channel.exchange_declare(exchange=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.name,
                                 exchange_type=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.type,
                                 durable=TRANSCRIPTION_RESULT_WAITING_EXCHANGE.durable)


def push(message,
         ttl_millis: Optional[int] = None,
         headers: Dict[str, str] = None,
         reply_to: Optional[str] = None,
         correlation_id: Optional[str] = None,
         delivery_mode: int = Publisher.DELIVERY_MODE_PERSISTENT):
    assert _initialized, 'Module not initialized, call __init__()'

    from .publisher import publisher

    publisher.push(message, ttl_millis=ttl_millis, headers=headers,
                   reply_to=reply_to, correlation_id=correlation_id,
                   delivery_mode=delivery_mode)


def push_to_routes(message, routes: List[Route],
                   ttl_millis: Optional[int] = None,
                   headers: Dict[str, str] = None,
                   reply_to: Optional[str] = None,
                   correlation_id: Optional[str] = None,
                   delivery_mode: int = Publisher.DELIVERY_MODE_PERSISTENT):
    assert _initialized, 'Module not initialized, call __init__()'

    from .publisher import publisher

    publisher.push_to_routes(message, routes=routes, ttl_millis=ttl_millis, headers=headers,
                             reply_to=reply_to, correlation_id=correlation_id,
                             delivery_mode=delivery_mode)


def close():
    publisher.close()
    consumer.close()


def consume(queue: Queue, dtype: Optional[Type] = None, exchange: Exchange = DEFAULT_EXCHANGE, auto_ack: bool = True):
    """
    Conventional decorator

    :param auto_ack: automatically ack the message. See @Consumer for details
    :param queue: queue to be consumed
    :param dtype: expected payload type
    :param exchange: exchange to bind the queue to
    :return: decorator
    """
    def decorator(func):
        assert _initialized, 'Module not initialized, call __init__()'
        assert _consumers_enabled, 'Consumers not enabled'

        from .consumer import consumer_manager

        queue_consumer = Consumer(queue=queue, exchange=exchange, dtype=dtype, callback=func, auto_ack=auto_ack)
        consumer_manager.add_consumer(queue_consumer)

    return decorator


def rpc_endpoint(queue: Queue, dtype: Optional[Type] = None, exchange: Exchange = DEFAULT_EXCHANGE):
    """
    Conventional decorator for declaring an rpc endpoint

    :param queue: queue to be consumed
    :param dtype: expected payload type
    :param exchange: exchange to bind the queue to
    :return: decorator
    """
    def decorator(func):
        assert _initialized, 'Module not initialized, call __init__()'
        assert _consumers_enabled, 'Consumers not enabled'

        from .rpc import rpc_manager

        queue_consumer = RpcConsumer(queue=queue, exchange=exchange, dtype=dtype, callback=func)
        rpc_manager.add_consumer(queue_consumer)

    return decorator


def rpc_call(route: Route,
             message: Any,
             timeout: Optional[float] = None,
             headers: Dict[str, str] = None,
             delivery_mode: int = Publisher.DELIVERY_MODE_PERSISTENT) -> Future:
    assert _initialized, 'Module not initialized, call __init__()'

    from .rpc import rpc_manager

    return rpc_manager.rpc_call(route=route,
                                message=message,
                                timeout=timeout,
                                headers=headers,
                                delivery_mode=delivery_mode)


def healthy() -> Tuple[bool, Dict[str, str]]:
    consumer_state: ConnectionState = consumer.get_connection_state()
    publisher_state: ConnectionState = publisher.get_connection_state()

    queue_healthy: bool = consumer_state == ConnectionState.CONNECTED and publisher_state == ConnectionState.CONNECTED

    return queue_healthy, {
        'CONSUMER': consumer_state.value,
        'PUBLISHER': publisher_state.value
    }
