import asyncio
from typing import Callable
import aioamqp
import aioredis
from .rmq import Rmq, DieAndRestartException
from .reply import Reply
from .message import Message

# from .reply import Reply
import ujson as json


class Consumer(object):
    def __init__(
        self,
        callback: Callable,
        queues: dict,
        host: str,
        login: str,
        password: str,
        redis_reply: aioredis.Redis,
        shared_rmq: Rmq,
        port: int = 5672,
        vhost: str = "/",
        login_method: str = "PLAIN",
    ) -> None:

        # Setting up configuration
        self.callback = callback
        self.queues = queues
        self.host = host
        self.login = login
        self.password = password
        self.port = port
        self.vhost = vhost
        self.login_method = login_method
        self.redis_reply = redis_reply
        self.shared_rmq = shared_rmq

    async def _callback(self, channel, body, envelope, properties):
        try:
            body = json.loads(body.decode())
            pm = Message(
                callback=self.callback,
                queue=envelope.routing_key,
                redis_reply=self.redis_reply,
                shared_rmq=self.shared_rmq,
            )
            loop = asyncio.get_event_loop()
            loop.create_task(pm.process(message=body))

            await asyncio.sleep(0.005)
            await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)
        except Exception as exc:
            print(f"ERROR, could not process message: {exc}")
            return

    async def consumer(self):
        try:
            rmq = Rmq(
                host=self.host,
                login=self.login,
                password=self.password,
                port=self.port,
                vhost=self.vhost,
                consumer=True,
            )
            for queue, queue_settings in self.queues.items():
                if queue_settings.get("active", True):
                    channel = await rmq.channel(
                        queue=queue, consumer=True, durable=True
                    )
                    await channel.basic_consume(
                        callback=self._callback, queue_name=queue
                    )

            while True:
                if rmq.protocol.state == 3:
                    await rmq.close()
                    return
                await asyncio.sleep(0.5)
        except aioamqp.AmqpClosedConnection:
            raise DieAndRestartException("Connection closed to RabbitMQ")
