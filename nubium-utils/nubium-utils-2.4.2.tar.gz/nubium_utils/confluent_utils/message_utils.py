import logging
from .confluent_runtime_vars import env_vars
from .producer_utils import confirm_produce

LOGGER = logging.getLogger(__name__)


def handle_no_messages(no_msg_exception=None, producers=None):
    """
    Since producer.poll() is typically called within the NU produce_message method, we want to acknowledge
    any outstanding produce attempts while the app has nothing to consume (and thus not actively producing/polling).
    """
    if no_msg_exception:
        LOGGER.debug(no_msg_exception)
    if producers:
        LOGGER.debug('flushing remaining producer queues')
        confirm_produce(producers)


def shutdown_cleanup(producers=None, consumer=None):
    """
    As part of shutdown, make sure all queued up produce messages are flushed, gracefully kill the consumer.
    """
    LOGGER.info('Performing graceful teardown of producer and/or consumer...')
    if consumer:
        LOGGER.debug("Shutting down consumer; no further commits can be queued or finalized.")
        consumer.close()
    if producers:
        LOGGER.debug("Sending/confirming the leftover messages in producer message queue")
        confirm_produce(producers, timeout=30)
