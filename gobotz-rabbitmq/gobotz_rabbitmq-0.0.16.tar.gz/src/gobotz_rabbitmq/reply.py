import aioredis
from .rmq import Rmq
import ujson as json


class Reply:
    def __init__(self, redis_reply: aioredis.Redis, shared_rmq: Rmq) -> None:
        self.redis_reply = redis_reply
        self.shared_rmq = shared_rmq
        self.msg_expiration = 5  # In seconds.

    async def send_redis(self, msg, queue) -> None:
        await self.redis_reply.setex(
            queue, self.msg_expiration, json.dumps(msg)
        )

    async def send(self, msg, queue) -> None:
        if not self.shared_rmq.connected:
            await self.shared_rmq.connect()

        channel = await self.shared_rmq.channel(
            queue=queue,
            consumer=False,
            durable=False,
            arguments={
                "x-message-ttl": self.msg_expiration * 1000,
                "x-expires": self.msg_expiration * 1000,
            },
        )
        await channel.basic_publish(
            payload=json.dumps(msg).encode(),
            exchange_name="",
            routing_key=queue,
            properties={
                "expiration": f"{self.msg_expiration * 1000}",
            },
        )
        await self.rmq.channel_close(channel, queue)
