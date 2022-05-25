from typing import Any
from dataclasses import dataclass, field

import pika

ExchangeName = "bloc_topic_exchange"


@dataclass
class RabbitMQ:
    user: str
    password: str
    host: str
    port: int
    v_host: str
    channel: Any = field(init=False)

    def __post_init__(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, port=self.port,
                # virtual_host=self.v_host,
                credentials=pika.PlainCredentials(
                    self.user, self.password)
            )
        )

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.exchange_declare(exchange=ExchangeName, exchange_type='topic', durable=True)

        self.channel = channel
    
    def consume_prepare(
        self, 
        queue_name: str,
        routing_key: str,
    ):
        self.channel.exchange_declare(exchange=ExchangeName, exchange_type='topic', durable=True)
        self.channel.queue_declare(queue_name, durable=True, exclusive=False, auto_delete=False)
        self.channel.queue_bind(exchange=ExchangeName, queue=queue_name, routing_key=routing_key)
