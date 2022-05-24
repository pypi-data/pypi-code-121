import asyncio
import aioamqp
from aioamqp.channel import Channel
from uuid import uuid4
from typing import Any, Dict, Optional
from time import time
import ujson as json


class ReplyTimeoutException(Exception):
    pass


class ReplyJsondecodeException(Exception):
    pass


class DieAndRestartException(Exception):
    pass


class Rmq(object):
    def __init__(
        self,
        host,
        login,
        password,
        port=5672,
        vhost="/",
        login_method="PLAIN",
        reply_method="rmq",
        redis=None,
        msg_expiration=5,
    ) -> None:

        # Setting up configuration
        self.host = host
        self.login = login
        self.password = password
        self.port = port
        self.vhost = vhost
        self.login_method = login_method
        self.reply_method = reply_method
        self.msg_expiration = msg_expiration
        if reply_method == "redis":
            assert (
                redis is not None
            ), "Redis connection required if reply_method set to redis"
            self.redis_reply = redis

        # Setting up RabbitMQ configuration
        self.transport = None
        self.protocol = None
        self.connected = False
        self.redis_reply = redis

    async def _connect(self) -> None:
        if self.connected:
            return
        self.transport, self.protocol = await aioamqp.connect(
            host=self.host,
            port=self.port,
            login=self.login,
            password=self.password,
            virtualhost=self.vhost,
            login_method=self.login_method,
        )
        if self.transport and self.protocol:
            self.connected = True

    async def _disconnect(self):
        if self.protocol:
            await self.protocol.close()
        if self.transport:
            self.transport.close()
        self.connected = False

    async def _channel(
        self,
        queue: str,
        consumer: bool = True,
        durable: bool = True,
        arguments: Dict = {},
    ) -> Channel:
        if not self.connected:
            self._connect()
        if queue not in self.defined_queues:
            self.defined_queues[queue] = await self.protocol.channel()
            await self.defined_queues[queue].queue(
                queue_name=queue, durable=durable, arguments=arguments
            )
            if consumer:
                await self.defined_queues[queue].basic_qos(
                    prefetch_count=1, prefetch_size=0, connection_global=False
                )
        return self.defined_queues[queue]

    async def _channel_close(self, channel: Channel, queue: str) -> None:
        await channel.close()
        del self.defined_queues[queue]

    async def _publish(
        self,
        message: Dict,
        queue: str,
        reply: bool,
        reply_async: bool,
        async_payload: Any,
        persistent: bool,
    ) -> Optional[Dict]:
        reply_to = f"reply-{uuid4()}"
        payload = {
            "msg_sent": int(time() * 1000),
            "reply_to": reply_to,
            "reply_method": self.reply_method,
            "reply_async": reply_async,
            "async_payload": async_payload,
            "message": message,
        }
        await self._publish_send(
            message=payload, queue=queue, persistent=persistent
        )

        if reply_async or not reply:
            return None

        if self.reply_method == "rmq":
            return await self._reply_rmq(reply_to=reply_to)

        if self.reply_method == "redis":
            return await self._reply_redis(reply_to=reply_to)

    async def _publish_send(
        self, message: Dict, queue: str, persistent: bool
    ) -> None:
        if not self.connected:
            self._connect()

        properties = {"content_type": "application/json"}
        if not persistent:
            properties["expiration"] = f"{self.msg_expiration * 1000}"

        channel = await self._channel(
            queue=queue, consumer=False, durable=True
        )
        await channel.basic_publish(
            payload=json.dumps(message),
            exchange_name="",
            routing_key=queue,
            properties=properties,
        )

    async def _reply_redis(self, reply_to):
        reply, aiosleep, timeout = None, float(0.05), float(0.05)
        while reply is None:
            timeout += aiosleep
            await asyncio.sleep(aiosleep)
            reply = await self.redis_reply.get(reply_to)
            if timeout >= float(self.msg_expiration):
                raise ReplyTimeoutException(
                    f"Timeout while waiting for reply from RabbitMQ: "
                    f"{self.msg_expiration} seconds"
                )

        try:
            return json.loads(reply)
        except Exception as exc:
            raise ReplyJsondecodeException(
                f"Could not decode JSON in reply: {exc}"
            )

    async def _reply_rmq(self, reply_to) -> Dict:
        rmq = Rmq(
            host=self.host,
            login=self.login,
            password=self.password,
            port=self.port,
            vhost=self.vhost,
            login_method=self.login_method,
            reply_method=self.reply_method,
            redis=self.redis_reply,
            msg_expiration=self.msg_expiration,
        )
        channel = await rmq.channel(
            queue=reply_to,
            consumer=True,
            durable=False,
            arguments={
                "x-message-ttl": self.msg_expiration * 1000,
                "x-expires": self.msg_expiration * 1000,
            },
        )
        reply, aiosleep, timeout = None, float(0.05), float(0.05)

        while reply is None:
            timeout += aiosleep
            await asyncio.sleep(aiosleep)
            try:
                reply = await channel.basic_get(queue_name=reply_to)
            except Exception:
                pass

            if timeout >= float(self.msg_expiration):
                await rmq.channel_close(channel, reply_to)
                await rmq.disconnect()
                raise ReplyTimeoutException(
                    f"Timeout while waiting for reply from RabbitMQ: "
                    f"{self.msg_expiration} seconds"
                )

        await rmq.channel_close(channel, reply_to)
        await rmq.disconnect()

        try:
            return json.loads(reply["message"].decode())
        except Exception as exc:
            raise ReplyJsondecodeException(
                f"Could not decode JSON in reply: {exc}"
            )

    async def connect(self) -> None:
        await self._connect()

    async def disconnect(self) -> None:
        await self._disconnect()

    async def channel(
        self,
        queue: str,
        consumer: bool = True,
        durable: bool = True,
        arguments: Dict = {},
    ) -> Channel:
        return await self._channel(
            queue=queue,
            consumer=consumer,
            durable=durable,
            arguments=arguments,
        )

    async def channel_close(self, channel: Channel, queue: str) -> None:
        await self._channel_close(channel=channel, queue=queue)

    async def publish(self, message: Dict, queue: str) -> None:
        await self._publish(
            message=message,
            queue=queue,
            reply=False,
            reply_async=False,
            async_payload=None,
            persistent=False,
        )

    async def publish_persistent(self, message: Dict, queue: str) -> None:
        await self._publish(
            message=message,
            queue=queue,
            reply=False,
            reply_async=False,
            async_payload=None,
            persistent=True,
        )

    async def publish_reply(self, message: Dict, queue: str) -> Dict:
        return await self._publish(
            message=message,
            queue=queue,
            reply=True,
            reply_async=False,
            async_payload=None,
            persistent=False,
        )

    async def publish_reply_async(
        self, message: Dict, queue: str, async_payload: Any
    ) -> None:
        await self._publish(
            message=message,
            queue=queue,
            reply=False,
            reply_async=True,
            async_payload=async_payload,
            persistent=False,
        )
