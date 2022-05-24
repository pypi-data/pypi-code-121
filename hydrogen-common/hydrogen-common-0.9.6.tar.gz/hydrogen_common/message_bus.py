"""
message_bus

    Defines a class to provide operations to use the message bus used by hydrogen.
    This is an abstraction to message bus that is implemented to use NAT, but the same
    abstrction could be used to implement with other message bus implementation.
"""
import os
import asyncio
import logging
import socket
import nats

NATS_PORT = os.getenv("NATS_PORT", "4222")
NATS_SERVER = os.getenv("NATS_SERVER", "localhost")


class MessageBus:
    """
    Service for reading and writing to the message bus.
    This insulates the caller from the choice of NATS as the message bus implementation
    and simplies the interface to what is used in the hydrogen project.

    Use the class as a context. For example, to publish a message on the bus.
        async with MessageBus() as bus:
            await bus.publish('message', 'body')

    This code must be within an async function that is called directly or indirectly from a
        asyncio.run(...method_or_function...)
    The above call can be made from anywhere such as a flask resource handler.
    """

    def __init__(self):
        """Constructor."""
        self.nc = None
        self.never = None

    async def __aenter__(self):
        """Python context asyncronous enter event. Create a NATS connection."""

        url = f"nats://{NATS_SERVER}:{NATS_PORT}"
        logging.debug(
            "Create MessageBus instance and connect to NATS server with with url '%s'.",
            url
        )
        self.nc = await nats.connect(url)
        logging.info("Successfully connected to NATS server '%s'", url)
        self.never = asyncio.Future()
        return self

    async def __aexit__(self, *args, **kwargs):
        """
        Python context asyncronous exit event.
        Wait for all NATS messages to process before exit.
        """

        await self.nc.flush()
        await self.nc.drain()

    async def publish(self, subject, message):
        """public an asyncronous message to the bus. The subject and message are strings."""

        logging.info("Publish subject '%s'", subject)
        logging.debug("Publish subject '%s' %s", subject, message)
        await self.nc.publish(subject, message.encode())

    async def request(self, subject, message, timeout=10):
        """Publish a synchronous message to the bus and return the reply."""

        logging.info("Request subject '%s'", subject)
        logging.debug("Request subject '%s' %s", subject, message)
        response = await self.nc.request(subject, message.encode(), timeout=timeout)
        return response.data.decode()

    async def subscribe(self, subject, cb):
        """
        Subscribe to receive message for a subject using a cb (callback method).
        The subject is also used as a queue so only one subscriber handles a message to allow for
        load balancing of messages.

        The callback is a callback function (it must be an async function, not a method in a class).
        """
        logging.info("Subscribe to subject '%s'.", subject)
        sid = await self.nc.subscribe(subject, cb=cb, queue=subject)
        return sid

    async def wait(self):
        """Wait forever while still listening for subscriptions."""

        hostname = socket.gethostname()
        logging.info("Wait for messages for '%s'.", hostname)
        await (self.never)
