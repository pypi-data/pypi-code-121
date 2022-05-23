import asyncio
import inspect
from typing import List

import aiokafka
from confluent_kafka import Consumer, KafkaException, KafkaError
from loguru import logger

from ..abstract_consumer import ConsumerMessageQueue
from ...configuration.kafka_settings import KafkaSettings

consumer = None


class KafkaConsumer(ConsumerMessageQueue):
    def __init__(self, bootstrap_servers, auto_offset_reset, group_id=None):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.confluent_config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': self.auto_offset_reset}

    kafka_settings = KafkaSettings()

    async def consume(self, topics: list,
                      process,
                      num_messages: int = kafka_settings.KAFKA_NUM_MESSAGES,
                      timeout: int = kafka_settings.KAFKA_DEFAULT_TIMEOUT) -> List or \
                                                                              None:
        try:
            assert self.group_id is not None
        except AssertionError:
            logger.error("Please make sure that you're providing the group id for confluent "
                         "consumer")
            logger.warning("Consumer did not start!")

            return

        consumer = Consumer(self.confluent_config)
        logger.info("Kafka consumer initialized")
        try:
            consumer.subscribe(topics)
            logger.info("Consuming : Listening to topics : {}".format(topics))
        except KafkaError as exc:
            logger.error("Exception during subscribing to topics - {}".format(exc))

        try:
            while True:
                msg = consumer.poll(timeout=0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        logger.error('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                    else:
                        logger.error("Error reading message : {}".format(msg.error()))
                        continue
                logger.info('Message received from topic {}, partition {}'.format(msg.topic(),
                                                                                  msg.partition()))
                await process(msg.value())
                consumer.commit()
        except KafkaException as e:
            logger.error('Message consuming failed: {}'.format(e.__str__()))
        finally:
            consumer.close()

    async def initialize_consumer(self, topics, **kwargs):
        logger.info("Starting consumer ...")
        loop = asyncio.get_event_loop()
        global consumer
        consumer = aiokafka.AIOKafkaConsumer(*topics, loop=loop,
                                             bootstrap_servers=self.bootstrap_servers,
                                             group_id=self.group_id,
                                             **kwargs)

        await consumer.start()
        logger.info("Consumer started successfully :)")

    async def send_consumer_message(self, consumer, process):
        logger.info("Consuming messages ...")
        try:
            async for msg in consumer:
                logger.info(f"Consumed msg: {msg.value}")
                await process(msg)
        except Exception as error:
            logger.error("Consumer error: {}".format(error))

    async def aio_consume(self, topics, process, **kwargs):
        try:
            assert inspect.iscoroutinefunction(process)
        except AssertionError:
            logger.error("Please make sure that you're providing a coroutine function (defined "
                         "with async)")
            logger.warning("Consumer did not start!")
            return

        await self.initialize_consumer(topics=topics, **kwargs)
        asyncio.create_task(self.send_consumer_message(consumer=consumer, process=process))

    def json_consume(self):
        pass
