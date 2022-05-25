from functools import wraps
import json
from typing import Callable

import pika.channel

from .blocking import RecoverableBlockingConsumerPublisher


class RabbitMQJob:
    def __init__(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
        publisher: "RecoverableBlockingConsumerPublisher",
    ):
        self.channel = channel
        self.method = method
        self.properties = properties
        self.body = body
        self.publisher = publisher

    def ack(self):
        self.channel.basic_ack(delivery_tag=self.method.delivery_tag)


class JSONRabbitMQJob(RabbitMQJob):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = json.loads(self.body.decode())

    @classmethod
    def from_job(cls, job: RabbitMQJob) -> 'JSONRabbitMQJob':
        return cls(
            channel=job.channel,
            method=job.method,
            properties=job.properties,
            body=job.body,
            publisher=job.publisher,
        )

    def retry(self):
        retry_count = self.message.get("retry_count") or 0
        self.message["retry_count"] = retry_count + 1
        body = json.dumps(self.message).encode()
        self.publisher.publish(exchange=self.method.exchange, routing_key=self.method.routing_key, body=body)

    def drop(self):
        if "retry_count" in self.message:
            del self.message["retry_count"]
        body = json.dumps(self.message).encode()
        self.publisher.publish(exchange=self.method.exchange, routing_key=f"{self.method.routing_key}.error", body=body)


def as_pika_callback(f: Callable[[RabbitMQJob], None], publisher):
    """
    Bridge a function taking a RabbitMQJob to a pika-compatible job callback

    :param f:               the function to wrap
    :param publisher:       the publisher to use to send back the job when needed
    :return:
    """

    @wraps(f)
    def wrapper(
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ):
        job = RabbitMQJob(channel, method, properties, body, publisher)
        return f(job)

    return wrapper
